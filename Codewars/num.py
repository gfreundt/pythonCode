def sort_by_guide(arr, guide):
    fixed = [arr[k] if i == -1 else None for k, i in enumerate(guide)]
    n = 1
    for k, i in enumerate(fixed):
        if not i:
            fixed[k] = arr[guide.index(n)]
            n += 1
    return fixed


arr = [56, 78, 3, 45, 4, 66, 2, 2, 4]
guide = [3, 1, -1, -1, 2, -1, 4, -1, 5]

print(sort_by_guide(arr, guide))

# the output should be [78,4,3,45,56,66,2,2,4]
