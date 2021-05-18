class NChickens:
    def __init__(self, n):
        self.count = 0
        self.N = n
        self.totalSafePlacements()
    def totalSafePlacements(self, row = 0, column = set(), major_diag = set(), minor_diag =set()):
            if row == self.N:
                self.count += 1
            for col in range(self.N):
                if row - col not in major_diag and row + col not in minor_diag and col not in column:
                    self.totalSafePlacements(row + 1, column.union({col}), major_diag.union({row - col}), minor_diag.union({row + col}))
n = int(input("Enter number of Chickens: "))
print(NChickens(n).count)
