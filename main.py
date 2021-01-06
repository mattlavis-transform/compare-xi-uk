import sys
from classes.classification import Classification


if __name__ == "__main__":
    if len(sys.argv) == 1:
        mode = "difference"
    else:
        if sys.argv[1] == "record":
            mode = "record"
        else:
            mode = "difference"

    if mode == "record":
        uk = Classification("uk")
        uk.run()
        xi = Classification("xi")
        xi.run()
    else:
        c = Classification("")
        c.compare()
