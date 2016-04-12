#!/usr/bin/env python

import sys
import csv

class Pin():
	def __init__(self, number, name, pin_type, direction, page, posx, posy):
		self.number = number
		self.name = name
		self.pin_type = pin_type
		self.direction = direction
		self.page = page
		self.posx = posx
		self.posy = posy

class Part():
	def __init__(self, name, ref, disp_number, disp_name, unit_count, unit_locked, part_type, csv_stream, out_stream):
		self.name = name
		self.ref = ref
		''' Y or N for text displayin '''
		self.disp_number = disp_number
		self.disp_name = disp_name
		''' Number of unit in the schematic part // Unit different = L same = F'''
		self.unit_count = int(unit_count)
		self.unit_locked = unit_locked
		'''part type: N (normal) P(power)'''
		self.part_type = part_type
		self.pin_list = []
		self.csv_stream = csv_stream
		self.out_stream = out_stream

	def write_pins_text(self):
		for pin in self.pin_list:
			pin_text = "X %s %s %s %s 50 %s 25 25 %s 1 %s\n" % (pin.name, pin.number, pin.posx, pin.posy, pin.direction, pin.page, pin.pin_type)
			self.out_stream.write(pin_text)

	def generate_pins(self):
		''' Pin Format: X name number posx posy length orientation Snum Snom unit convert Etype [shape] '''
		index = 0
		p_index = 0
		page_dict = dict()
		posy = []
		posx = []
		for i in range(0, self.unit_count + 1):
			posy.append(0)
			posx.append(0)
		for row in self.csv_stream.data:
			if (index != 0):
				pin_number = row[self.csv_stream.pack_col_index]
				if (self.unit_count > 1):
					pin_page = row[self.csv_stream.page_col_index]
				else:
					pin_page = "1"
				pin_name = row[self.csv_stream.name_col_index]
				pin_type = self.get_pin_type(row[self.csv_stream.type_col_index])
				if(pin_number != "0"):
					if (self.csv_stream.has_dir == 1):
						direction = row[self.csv_stream.direc_col_index]
					else:
						direction = "L"
					
					if(pin_page in page_dict):
						page_dict[pin_page] = page_dict[pin_page] + 1
						p_index = page_dict[pin_page]
					else:
						page_dict[pin_page] = 1
						p_index = 1
					
					''' For the moment we will only prepare the file for editing '''
					''' posy = ((p_index * -1) - 1) * 50
					posx = 100'''
					page_num = int(pin_page)
					if (direction == "L" or direction == "R"):
						posy[page_num] = posy[page_num] - 50
					else:
						posx[page_num] = posx[page_num] +50
					self.pin_list.append(Pin(pin_number, pin_name, pin_type, direction, pin_page, posx[page_num], posy[page_num]))
					print(pin_number)
					
			index = index + 1
		pass

	def get_pin_type(self, pin_type_csv):
		pin_type = pin_type_csv
		if (pin_type == "I/O"):
			pin_type = "B"
		elif (pin_type == "I"):
			pin_type = "I"
		elif (pin_type == "O"):
			pin_type = "O"
		elif (pin_type == "S"):
			pin_type = "W"
		else:
			pin_type = "B"
		return pin_type

	def write_header_text(self):
		''' replace with date '''
		header_text = "EESchema-LIBRARY Version 2.3  Date: 17/06/2012 19:45:46\n"
		''' Define the general settings of the component '''
		header_text += "DEF %s %s 0 40 %s %s %s %s %s\n" % (self.name, self.ref, self.disp_number, self.disp_name, self.unit_count, self.unit_locked, self.part_type)
		''' F0 = reference F1 = name the user will place it in the kicad editor'''
		header_text += "F0 \"%s\" 0 0 50 H V C CNN\n" % (self.ref)
		header_text += "F1 \"%s\" 0 0 50 H V C CNN\n" % (self.name)
		header_text += "DRAW\n"
		self.out_stream.write(header_text)

	def write_footer_text(self):
		footer_text = "ENDDRAW\nENDDEF\n#\n#End Library"
		self.out_stream.write(footer_text)

class ExcelDefaultFR(csv.excel):
	delimiter = ";"

class CSV_Utils():
	def __init__(self, fname, package):
		self.fname = fname
		self.current_line = 0
		self.package = package
		self.has_dir = 0

	def read_file(self):
		datafile = open(self.fname, "r")
		''' render the csv data subscriptable '''
		self.data = list(csv.reader(datafile, ExcelDefaultFR()))
		datafile.close()
		return self.check_csvdata()

	def check_csvdata(self):
		self.header = self.data[0]
		if self.package in self.header:
			print("Package %s found\n" % self.package)
			package_page = "%s_PAGE" % self.package
			if package_page in self.header:
				self.pack_col_index = self.header.index(self.package)
				self.page_col_index = self.header.index(package_page)
				self.name_col_index = self.header.index("NAME")
				self.type_col_index = self.header.index("TYPE")
				if "PIN_DIRECTION" in self.header:
					self.direc_col_index = self.header.index("PIN_DIRECTION")
					self.has_dir = 1
				return 1
		print("Please correct your CSV file Header\n")
		return 0

class OutFile():
	def __init__(self, fname):
		self.filename = fname
		pass

	def write(self, buffer):
		self.file.write(buffer)

	def open_out_file(self):
		self.file = open(self.filename, "w")

	def close_file(self):
		self.file.close()

class Utils():
	def __init__(self):
		pass
	
	''' kicad_unit = int(mm * 39.3700787402 * 10) '''
	@staticmethod
	def get_kicad_unit(mm):
		print("mm: %s - kicad: %s\n" % (mm, (mm * 39.3700787402 * 10.0)))
		return (mm * 39.3700787402 * 10.0)

def main():
	if len(sys.argv) < 3:
		print("python csv2lib.py datafile package part_name unit_count ref outfile\n")
		sys.exit(2)
	fname = sys.argv[1]
	package = sys.argv[2]
	part_name = sys.argv[3]
	unit_count = sys.argv[4]
	ref = sys.argv[5]
	outfile = sys.argv[6]
	csv_stream = CSV_Utils(fname, package)
	if (csv_stream.read_file() != 1):
		sys.exit(2)
	out_stream = OutFile(outfile)
	out_stream.open_out_file()
	part = Part(part_name, ref, "Y", "Y", unit_count, "L", "N", csv_stream, out_stream)
	part.write_header_text()
	part.generate_pins()
	part.write_pins_text()
	part.write_footer_text()
	out_stream.close_file()

if __name__ == '__main__':
	main()

