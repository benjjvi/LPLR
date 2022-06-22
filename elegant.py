def ElegantExit(code):
    if code == 0:
        exit()
    # Exit code. This is useful for informative error messages.
    reasons = {
        101: "101 Unsupported OS architecture.",
        102: "102 Programming Error",
        103: "103 Not Enough Resources",
        104: "104 Variable Not Acceptable",
        105: "105 Variable assigned too low or high that it could cause undesirable actions"
    }
    
    print("We're sorry, and error has occured.")
    print(f"We were provided with error code {code}.")
    if code in reasons:
        print("We have found a reason for this exit.")
        print(reasons[code])
    else:
        print("We cannot find a reason for this error. Please email ben@bildsben.com for help resolving this issue.")