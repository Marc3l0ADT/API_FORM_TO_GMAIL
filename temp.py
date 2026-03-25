import csv 


with open('tablas/cords.csv') as csvfile:
    reader = csv.reader(csvfile)
    cordenadas = list(reader)
for i in cordenadas[1:]:
    i.append('no')
with open('tablas/cords.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(cordenadas)