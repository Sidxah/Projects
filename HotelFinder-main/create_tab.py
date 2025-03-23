# open a file for read - only purposes
f = open ("hotels.csv", 'r')
m = open ("hoteldb-schema.sql" , 'w')
m.write("CREATE TABLE metros ( \n")
# skip the first line which contains the attribute names

line = next(f)
# break line into an array of attributes separated by ';'
items = line . rstrip ("\n"). split (",")
# num_attributes = number of attributes in this line
num_attributes = len ( items )
# loop over each attribute in the array items
i = 0
comma = ","
while i < num_attributes :
    # replace ' with '', for strings in postgreSQL
    item = items [i]. replace ("'", " ''")
    # replace , with space for the last attribute
    if i == (num_attributes - 1) :
        comma = " "
    # make a string varible with the attribute value
    if (item == "prix" or item == "telephone" or item == "departement" or item == "cp" or item == "capacite" or item == "nbr_chambre"):
        string_to_print = item + " NUMERIC(10,0) " + comma
    
    elif (item == "geo_x" or item == "geo_y"):
        string_to_print = item + " NUMERIC(10, 6) " + comma
    else :
        string_to_print = item + " TEXT" + comma
    # print the string
    m.write( string_to_print + "\n" )
    i = i + 1

m.write(");\n")
f.close()
m.close()
