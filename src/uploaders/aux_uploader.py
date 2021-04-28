

class AuxUploader:

    def __init__(self, conn, cursor): 
        self.conn = conn
        self.cursor = cursor

    def start(self) : 
        #self.__create_rank_filter_table()
        self.__create_degree_selection()

    def __create_rank_filter_table(self): 
        list_to_upload = [ (x,) for x in list(range(1,100)) ]
        query = "INSERT INTO powertracks.rank_filter VALUES (?)"
        self.cursor.executemany(query, list_to_upload)
        self.cursor.commit()

    def __create_degree_selection(self):

        list_to_upload = []
        for i in range(-90, 0) : 
            list_to_upload.append( (i, i+360) )
        for i in range(0, 361) : 
            list_to_upload.append( (i, i))

        query = "INSERT INTO powertracks.degree_selection VALUES (?,?)"
        self.cursor.executemany(query, list_to_upload)
        self.cursor.commit()