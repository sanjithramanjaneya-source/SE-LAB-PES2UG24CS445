# Lab 5: Static Code Analysis — Issue Report

## Issues Identified Before Fixing

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Weak MD5 hash | Security — High | 25 | The original code used MD5 to generate ticket codes. MD5 is not recommended for security-sensitive hashing. | Replaced MD5 with SHA-256 to generate ticket codes. |
| Permissive file permissions | Security — High | 55 | The original code used permissions 0777, allowing everyone to read, write, and execute the file. | Changed permissions to 0600 to restrict access to the file owner. |
| Mutable default argument | Code Quality — Medium | 9 | The original function used an empty list as a default argument. The list could be shared across function calls. | Changed the default to None and created a new list inside the function. |
| Bare exception | Code Quality — Medium | 21 | The original code used a bare except clause, which could hide unexpected errors. | Replaced it with specific exceptions such as KeyError and ValueError. |
| Missing function docstrings | Code Quality — Low | Multiple | Several functions did not explain their purpose. | Added docstrings describing the functions. |
| Incorrect naming convention | Code Style — Low | 37 | The function printSeatingSummary did not follow Python's snake_case naming convention. | Renamed it to print_seating_summary. |
| Long lines | Code Style — Low | 40 | Some lines exceeded the recommended line length. | Split long statements across multiple lines. |
| File handling without context managers | Code Quality — Low | 28, 33 | Files were opened without using a context manager, making resource management less reliable. | Used the with open(...) statement to manage files safely. |

## Summary

The original program was analysed using Pylint, Flake8, and Bandit. The identified issues covered security, code quality, and coding style.

The code was subsequently modified to address these issues. The three tools were run again to evaluate the improvements.