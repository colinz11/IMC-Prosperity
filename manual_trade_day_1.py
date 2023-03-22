import math

max_score = 1
path = ""


rates = [[1,0.5,1.45,0.75], [1.95,1, 3.1, 1.49], [0.67, 0.31, 1, 0.48], [1.34, 0.64, 1.98, 1]]

def arbitrage(current_product, current_state, price_so_far, curr_path, max_val):
	global max_score
	global path
	if current_state >= max_val:
		curr_price = price_so_far*rates[current_product][3]
		# print("current price", curr_price)
		if max_score < curr_price:
			path = curr_path + str(current_product) + "3"
			max_score = curr_price
		return
	for i in range(4):
		arbitrage(i, current_state+1, price_so_far*rates[current_product][i], curr_path+str(current_product), max_val)


for i in range(0,5):
	arbitrage(3, 0, 1, "", i)

print(max_score)
print(path)