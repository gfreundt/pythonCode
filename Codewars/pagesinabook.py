def amount_of_pages(summary):
    n = 1
    pages = 0
    while True:
        pages += len(str(n))
        if pages >= summary:
            return n
        n += 1


f = amount_of_pages(1095)

print(f)
