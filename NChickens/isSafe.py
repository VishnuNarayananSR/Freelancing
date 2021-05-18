class NChickens:
    def __init__(self,n):
        self.N = n
        self.field = [[0] * n for _ in range(n)]
    def set_field(self, row, col):
        self.field[row][col] = 1
    def isSafe(self):
        row = set()
        column = set()
        major_diag = set()
        minor_diag = set()
        for i in range(self.N):
            for j in range(self.N):
                if (self.field[i][j]):
                    if(i in row or j in column or i - j in major_diag or i + j in minor_diag):
                        return "Attack"
                    else:
                        row.add(i)
                        column.add(j)
                        major_diag.add(i - j)
                        minor_diag.add(i + j)
        return "Safe"

n = int(input("Enter no of chickens"))
obj = NChickens(n)
print("Enter field Placement")
for i in range(n):
    row, col = map(int, input().split()) 
    obj.set_field(row, col)
print(obj.isSafe())