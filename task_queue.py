from multiprocessing import Pool

def OCRimage(file_name):
    print("file_name = %s" % file_name)

filterfiles = ["image%03d.tif" % n for n in range(5)]

pool = Pool(processes=2)
result = pool.map(OCRimage, filterfiles)

pool.close()
pool.join()