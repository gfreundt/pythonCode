import kivymd

from kivymd.uix.datatables import MDDataTable

g = dir(MDDataTable)

for i in g:
    if "inc" in i:
        print(help(i))
