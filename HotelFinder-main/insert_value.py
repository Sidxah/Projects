# open a file for read - only purposes
f = open ("hotels.csv", 'r')
# open a file for append mode
m = open ("hoteldb-data.sql" , 'w')

# skip the first line which contains the attribute names
next (f)
       
# loop over each line of the input file f
for line in f:
    # Ajout de la ligne (line)
    m.write("\nINSERT INTO metros VALUES (\n")
    # break line into an array of attributes separated by ';'
    items = line . rstrip ("\n"). split (",")
    
    # num_attributes = number of attributes in this line
    num_attributes = len ( items )
    # loop over each attribute in the array items
    i = 0
    comma = ","
    while i < num_attributes :
        if i == num_attributes - 1 : 
            comma = " "
        
       
        # replace ' with '', for strings in postgreSQL
        item = items [i]. replace ("'", " ''")
        # make a string varible with the attribute value
        string_to_print = "'" + item + "'" + comma
        # print the string
        m.write( string_to_print )
        i = i + 1
        if i == (num_attributes) :
            m.write(");\n")
        
    
  
