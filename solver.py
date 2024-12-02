import sys

def verify_elements(matrix):
    return all(all(el in {'?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '.'} for el in row) for row in matrix)

with open(sys.argv[1], "r") as file:
    board = file.read().strip()
    board = list(map(lambda s : s.split(' '), board.split('\n')))

    # Ensure the board is properly rectangular
    if board == []:
        print("The board is empty!")
        exit(1)
    
    lengths = list(map(len, board))

    n = lengths[0]
    for x in lengths:
        if x != n:
            print("Inconsistent row lengths!")
            exit(1)

    m = len(board)

    # Verify each of the characters is allowed
    if not verify_elements(board):
        print("Characters must only be '.', '?' or an integer from 1 to 8")
        exit(1)

    # Generate the Singular variable names 
    vars = []

    for i in range(m):
        for j in range(n):
            k = i*n + j
            vars.append('x' + str(k))

    singular_lines = [
            "option(redSB)",
            "ring R = 0, (" + ", ".join(vars) + "), dp",
        ]

    poly_count = 0
    reduces = []

    unknown = lambda c : c == '.' or c == '?'

    for i in range(m):
        for j in range(n):
            k = n*i + j
            if unknown(board[i][j]):
                domain_poly = f"poly h{poly_count} = x{k} * (x{k} - 1)"
                singular_lines.append(domain_poly)
                poly_count += 1

                if board[i][j] == '?':
                    reduces.append(f"reduce(x{k}, SI)")

                continue

            # Otherwise, we know board[i][j] is a number
            # So we add the corresponding restriction
            x = int(board[i][j])

            neighboring_cells = []

            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if (i + di < 0 or i + di >= m): continue
                    if (j + dj < 0 or j + dj >= n): continue
                    if (di == 0 and dj == 0): continue
                    
                    if not unknown(board[i + di][j + dj]): continue
                    neighboring_cells.append((i + di, j + dj))

            coords = map(lambda p : "x" + str(n * p[0] + p[1]), neighboring_cells)
            poly = f"poly h{poly_count} = " + " + ".join(coords)
            poly += " - " + str(x)
            singular_lines.append(poly)
            poly_count += 1

    if poly_count == 0:
        ideal_line = "ideal I = 0"
    else:
        ideal_line = "ideal I = " + ", ".join(map(lambda i : "h" + str(i), range(poly_count)))

    singular_lines.append(ideal_line)
    singular_lines.append("ideal SI = std(I)")

    singular_lines = singular_lines + reduces

    output = ";\n".join(singular_lines) + ";"
    print(output)
