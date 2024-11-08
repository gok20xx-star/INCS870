import capstone
import json
import os
import pefile
from elftools.elf.elffile import ELFFile
from pathlib import Path


# Function to extract PE headers and disassemble code sections
def process_pe_file(file_path, all_pe_data):
    try:
        pe = pefile.PE(file_path)

        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Extract raw header
        dos_header_dict = {
            "e_magic": hex(pe.DOS_HEADER.e_magic),
            "e_cblp": hex(pe.DOS_HEADER.e_cblp),
            "e_cp": hex(pe.DOS_HEADER.e_cp),
            "e_crlc": hex(pe.DOS_HEADER.e_crlc),
            "e_cparhdr": hex(pe.DOS_HEADER.e_cparhdr),
            "e_minalloc": hex(pe.DOS_HEADER.e_minalloc),
            "e_maxalloc": hex(pe.DOS_HEADER.e_maxalloc),
            "e_ss": hex(pe.DOS_HEADER.e_ss),
            "e_sp": hex(pe.DOS_HEADER.e_sp),
            "e_csum": hex(pe.DOS_HEADER.e_csum),
            "e_ip": hex(pe.DOS_HEADER.e_ip),
            "e_cs": hex(pe.DOS_HEADER.e_cs),
            "e_lfarlc": hex(pe.DOS_HEADER.e_lfarlc),
            "e_ovno": hex(pe.DOS_HEADER.e_ovno),
            "e_oemid": hex(pe.DOS_HEADER.e_oemid),
            "e_oeminfo": hex(pe.DOS_HEADER.e_oeminfo),
            "e_lfanew": hex(pe.DOS_HEADER.e_lfanew)  # This points to the NT Headers
        }

        # Extract the NT Header (File Header) fields
        nt_header_dict = {
            "Machine": hex(pe.FILE_HEADER.Machine),
            "NumberOfSections": pe.FILE_HEADER.NumberOfSections,
            "TimeDateStamp": hex(pe.FILE_HEADER.TimeDateStamp),
            "PointerToSymbolTable": hex(pe.FILE_HEADER.PointerToSymbolTable),
            "NumberOfSymbols": pe.FILE_HEADER.NumberOfSymbols,
            "SizeOfOptionalHeader": pe.FILE_HEADER.SizeOfOptionalHeader,
            "Characteristics": hex(pe.FILE_HEADER.Characteristics)
        }

        # Extract the Optional Header fields
        optional_header_dict = {
            "Magic": hex(pe.OPTIONAL_HEADER.Magic),
            "EntryPointAddress": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
            "ImageBase": hex(pe.OPTIONAL_HEADER.ImageBase),
            "SectionAlignment": hex(pe.OPTIONAL_HEADER.SectionAlignment),
            "FileAlignment": hex(pe.OPTIONAL_HEADER.FileAlignment),
            "Subsystem": pe.OPTIONAL_HEADER.Subsystem,
            "DllCharacteristics": hex(pe.OPTIONAL_HEADER.DllCharacteristics),
            "SizeOfImage": hex(pe.OPTIONAL_HEADER.SizeOfImage),
            "SizeOfHeaders": hex(pe.OPTIONAL_HEADER.SizeOfHeaders),
            "SizeOfStackReserve": hex(pe.OPTIONAL_HEADER.SizeOfStackReserve),
            "SizeOfStackCommit": hex(pe.OPTIONAL_HEADER.SizeOfStackCommit),
            "SizeOfHeapReserve": hex(pe.OPTIONAL_HEADER.SizeOfHeapReserve),
            "SizeOfHeapCommit": hex(pe.OPTIONAL_HEADER.SizeOfHeapCommit),
            "LoaderFlags": hex(pe.OPTIONAL_HEADER.LoaderFlags),
            "NumberOfRvaAndSizes": pe.OPTIONAL_HEADER.NumberOfRvaAndSizes
        }

         # Extract Section headers
        section_headers = []
        for section in pe.sections:
            section_data = {
                "Name": section.Name.decode('utf-8').strip('\x00'),
                "VirtualAddress": hex(section.VirtualAddress),
                "SizeOfRawData": hex(section.SizeOfRawData),
                "PointerToRawData": hex(section.PointerToRawData),
                "Characteristics": hex(section.Characteristics)
            }
            section_headers.append(section_data)

        # Combine all headers into one dictionary
        pe_headers_dict = {
            "File_Hash": file_name,
            "DOS_Header": dos_header_dict,
            "NT_Header": nt_header_dict,
            "Optional_Header": optional_header_dict,
            "Section_Headers": section_headers
        }
        pe_headers_json = json.dumps(pe_headers_dict, indent=4)

        all_pe_data.append(pe_headers_dict)

    except Exception as e:
        print(f"[PE] Error processing file {file_path}: {e}")


# Function to extract ELF headers and disassemble code sections
def process_elf_file(file_path, all_elf_data):
    try:
        with open(file_path, 'rb') as f:
            elf = ELFFile(f)

            file_name = os.path.splitext(os.path.basename(file_path))[0]

            elf_header_dict = {
                "EI_CLASS": elf.header['e_ident']['EI_CLASS'],
                "EI_DATA": elf.header['e_ident']['EI_DATA'],
                "EI_VERSION": elf.header['e_ident']['EI_VERSION'],
                "EI_OSABI": elf.header['e_ident']['EI_OSABI'],
                "Type": elf.header['e_type'],
                "Machine": elf.header['e_machine'],
                "Version": elf.header['e_version'],
                "EntryPointAddress": hex(elf.header['e_entry']),
                "ProgramHeaderOffset": hex(elf.header['e_phoff']),
                "SectionHeaderOffset": hex(elf.header['e_shoff']),
                "Flags": hex(elf.header['e_flags']),
                "HeaderSize": elf.header['e_ehsize'],
                "ProgramHeaderEntrySize": elf.header['e_phentsize'],
                "ProgramHeaderCount": elf.header['e_phnum'],
                "SectionHeaderEntrySize": elf.header['e_shentsize'],
                "SectionHeaderCount": elf.header['e_shnum'],
                "SectionHeaderStringTableIndex": elf.header['e_shstrndx']
            }

            # Extract the Program Header fields
            program_headers = []
            for i in range(elf.num_segments()):
                segment = elf.get_segment(i)
                program_headers.append({
                    "Type": segment['p_type'],
                    "Offset": hex(segment['p_offset']),
                    "VirtualAddress": hex(segment['p_vaddr']),
                    "PhysicalAddress": hex(segment['p_paddr']),
                    "FileSize": hex(segment['p_filesz']),
                    "MemorySize": hex(segment['p_memsz']),
                    "Flags": hex(segment['p_flags']),
                    "Alignment": hex(segment['p_align'])
                })

            # Extract the Section Header fields
            section_headers = []
            for i in range(elf.num_sections()):
                section = elf.get_section(i)
                section_headers.append({
                    "Name": section.name,
                    "Type": section['sh_type'],
                    "Flags": hex(section['sh_flags']),
                    "Address": hex(section['sh_addr']),
                    "Offset": hex(section['sh_offset']),
                    "Size": hex(section['sh_size']),
                    "Link": section['sh_link'],
                    "Info": section['sh_info'],
                    "AddressAlignment": hex(section['sh_addralign']),
                    "EntrySize": hex(section['sh_entsize'])
                })

            # Combine all headers into one dictionary
            elf_headers_dict = {
                "ELF_Hash": file_name,
                "ELF_Header": elf_header_dict,
                "Program_Headers": program_headers,
                "Section_Headers": section_headers
            }

            all_elf_data.append(elf_headers_dict)

    except Exception as e:
        print(f"[ELF] Error processing file {file_path}: {e}")


# Process a list of malware files
def process_files(file_list, filetype):
    all_pe_data = []
    all_elf_data = []
    for file_path in file_list:
        if file_path.endswith(".exe"):
            process_pe_file(file_path, all_pe_data)
        elif file_path.endswith(".elf"):
            process_elf_file(file_path, all_elf_data)
        else:
            print(f"Unknown file format: {file_path}")
    with open(current_dir.parent / "result" / filetype/ "pe_headers", 'w') as json_file:
        json.dump(all_pe_data, json_file, indent=4)

    with open(current_dir.parent / "result" / filetype/ "elf_headers", 'w') as json_file:
                json.dump(all_elf_data, json_file, indent=4)


def collect_files(directory):
    # List to hold the full file paths for PE and ELF files
    malware_files = []

    # Walk through the directory and all subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a PE or ELF file based on extension
            if file.endswith(".exe") or file.endswith(".elf"):
                # Get the full path of the file
                full_path = os.path.join(root, file)
                malware_files.append(full_path)

    return malware_files

current_dir = Path(__file__)
malware_directory = current_dir.parent / "Malware"
benign_directory = current_dir.parent / "Benign"
# print(malware_directory)
malware_files = collect_files(malware_directory)
benign_files = collect_files(benign_directory)

# print(benign_directory)
process_files(malware_files, "Malware")
process_files(benign_files, "Benign")
