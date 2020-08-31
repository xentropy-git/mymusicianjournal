table_name = 'this_table'
table_dict = {
    'poop_key': 'INTEGER NOT NULLPRIMARY KEY',
    'email': 'text'
    }

column_definitions = ', '.join(['%s %s' % (x,y) for x, y in table_dict.items()])
query_txt =  'CREATE TABLE %s(%s);' % (table_name, column_definitions)

print (query_txt)
