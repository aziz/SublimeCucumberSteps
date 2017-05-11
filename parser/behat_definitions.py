# ./bin/behat -c ./tests/acceptance/behat.yml -p abargi -di --no-ansi
#
import codecs
from os import path, walk

root = '/Users/allen/TicketMaster/mnxweb'
TEST_FOLDER = 'tests/acceptance/bootstrap'
IGNORED_FILES = ['.DS_Store']

def find(string):
    search_path = path.join(root, TEST_FOLDER)
    for xroot, dirs, files in walk(search_path):
        for f in files:
            ignored = False
            for ignore_file in IGNORED_FILES:
                if f == ignore_file:
                    ignored = True
            if ignored:
                continue
            file_path = path.join(xroot, f)
            line_number = 0
            for line in codecs.open(file_path, 'r', 'utf-8'):
                line_number = line_number + 1
                if string in line:
                    print(line)
                    print(file_path)
                    print(line_number)

# find('/^the user have an adblock extension enabled in the browser$/')
