import numpy as np



def score(board, method):
	if method == 'soltis':
		scoring = (0,9,4.5,3,3,1)
	elif method == 'kaufman':
		scoring = (0,9.75,5,3.25,3.25,1)
	response = []
	for color, sign in zip(['white','black'],(1, -1)):
		total = 0
		for x in range(8):
			for y in range(8):
				if board[(x,y)] / sign > 0:
					piece = abs(board[(x,y)])
					total += scoring[piece-1]
		response.append(total)			
	return response




def main():
	board=np.zeros((8,8))
	w,b = soltis(board)
	print(w,b)


if __name__ == '__main__':
	main()