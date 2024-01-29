import io
import os

from gui.helpers.ect import mh_ae, gm_ae


class File_Interact():
    def __init__(self, file_name):
        self.file_name = file_name

    def write_file(self, ndung):
        f = io.open(self.file_name, 'w', encoding = 'utf-8')
        f.write(ndung)
        f.close()

    def write_file_maHoaAES(self, ndung):
        f = io.open(self.file_name, 'w', encoding = 'utf-8')
        f.write(mh_ae(ndung))
        f.close()

    def read_file_maHoaAES(self):
        f = io.open(self.file_name, 'r', encoding = 'utf-8')
        ndung = f.read()
        f.close()
        return gm_ae(ndung)

    def write_file_from_list(self, list_lines):
        f = io.open(self.file_name, 'w', encoding = 'utf-8')
        f.write('\n'.join(list_lines))
        f.close()

    def replace_line_in_file(self, i_line, new_line):
        L = self.read_file_list()
        L2 = L.copy()
        L2[i_line] = new_line
        self.write_file_from_list(L2)

    def write_file_line(self, ndung_line):
        f = io.open(self.file_name, 'a', encoding = 'utf-8')
        f.write('%s\n' % ndung_line)
        f.close()

    def read_file(self):
        f = io.open(self.file_name, 'r', encoding = 'utf-8')
        ndung = f.read()
        f.close()
        return ndung

    def read_file_list(self):
        f = io.open(self.file_name, 'r', encoding = 'utf-8')
        ndung = f.read()
        f.close()
        return ndung.split('\n')

    def remove_all_file_in_directory(self, folder_path):
        list_file = ['%s/%s' % (folder_path, file_name) for file_name in os.listdir(folder_path)]
        for file in list_file:
            os.remove(file)
