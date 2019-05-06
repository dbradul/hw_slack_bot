import re
import random
import math

#---------------------------------------------------------------
test_set_01 = (
    ((1, 2, 3),  4),
    ((-1, 0, 999999), -1)
)

test_set_08 = (
    (("Mark Zuckerberg",),  "Zuckerberg Mark"),
)

test_set_09 = (
    (("employee_first_name",),  "EmployeeFirstName"),
)

test_set_10 = (
    (("Leo Tolstoy*1828-08-28*1910-11-20",),  "Leo Tolstoy, 82"),
    (("Albert Einstein*1879-03-14*1955-04-18",),  "Albert Einstein, 76"),
)

test_set_11 = (
    ((45,), 0.7853981633974483),
    ((60,), 1.0471975511965976),
    ((30,), 0.5235987755982988),
)

test_set_12 = (
    ((123,), 6),
    ((999,), 27),
    ((100,), 1),
)
#
# test_set_13 = (
#     ((3,4), (6, 12)),
# )

test_set_13 = (
    ((1, 1),    (7.5844755917, 1.0471975512)),
    ((100, 100),(75844.7559174816, 1047197.5511966)),
    ((1, 100),  (317.3165655832, 104.7197551197)),
    ((100, 1),  (62833.4238288547, 10471.975511966)),
    ((5, 42),   (742.9328151279, 1099.5574287564)),
)

test_set_14 = (
    ((3,), False),
    ((4,), True),
)

test_set_15 = (
    # inside
    ((0,0,5, 0,0,4), False),
    ((0,0,4, 0,0,5), False),
    ((0,0,5, 0,1,1), False),
    ((0,0,5, 1,1,1), False),
    ((0,1,1, 0,0,5), False),

    # coinside
    ((0,0,4, 0,0,4), True),
    ((1, 1, 42, 1, 1, 42), True),

    # touch
    ((0,0,1, 2,0,1), True),
    ((2,0,1, 0,0,1), True),
    ((2, 2, 2, 5, 2, 1), True),
    ((2, 2, 2, 2, 5, 1), True),

    # intersection
    ((0,0,2, 0,1,2), True),
    ((0,0,2, 0,0.2,1.91), True),
    ((0,1,2, 0,0,2), True),
    ((2, 2, 2, 4, 4, 2), True),

    # far away from each other
    ((0, 0, 1, 0, 10, 2), False),
    ((0, 0, 1, 3, 3, 1), False),
)

test_set_16 = (
    ((5,6), False),
    ((4,6), True),
)

test_set_17 = (
    ((5,2,1), (None, None)),
    ((1,2,1), (-1, None)),
    ((2, 2, 1), (None, None)),
    ((2, -1, 0), (0.5, 0.0)),
    ((10, 2, 0), (0, -0.2)),
    ((2, 4, 2), (-1.0, None)),
)

test_set_18 = (
    (('x','x'), 120),
    (('x','z'), 363),
    (('a', 'z'), 2847),
)


test_set_21 = (
    ((769661855331,), 9),
    ((733764839249,), 9),
    ((945590851463,), 9),
    ((568504332454,), 8),
    ((100000000000,), 1),
    ((123456054321,), 6),
)

test_set_24 = (
    ((('A A', 'A B', 'A C', 'A D'),), (4, 0, 0, 0)),
    ((('A I', 'B J', 'C T', 'D U'),), (1, 1, 1, 1)),
    ((('Johnny Depp',
     'Al Pacino',
     'Kevin Spacey',
     'Denzel Washington',
     'Russell Crowe',
     'Brad Pitt',
     'Angelina Jolie',
     'Leonardo DiCaprio',
     'Tom Cruise',
     'John Travolta',
     'Arnold Schwarzenegger',
     'Sylvester Stallone',
     'Kate Winslet',
     'Christian Bale',
     'Morgan Freeman',
     'Keanu Reeves',
     'Hugh Jackman',
     'Edward Norton',
     'Bruce Willis',
     'Tom Hanks',
     'Charlize Theron',
     'Will Smith',
     'Sean Connery',
     'Keira Knightley',
     'Vin Diesel',
     'Matt Damon',
     'Richard Gere',
     'Catherine Zeta-Jones',
     'Clive Owen',
     'Mel Gibson',
     'George Clooney',
     'Jack Nicholson',
     'Scarlett Johansson',
     'Tom Hardy',
     'Samuel Jackson',
     'Sandra Bullock',
     'Meg Ryan',
     'Nicole Kidman',
     'Simon Baker',
     'Cameron Diaz',
     'Anthony Hopkins'),), (18, 11, 8, 4)),
)


test_set_23 = (
    ((), (20, 1048575)),
)

test_set_25 = (
    (([x for x in range(1,100,2)],), lambda result: (1 - sum(1 for idx, elem in enumerate(result) if elem==idx+1) / len(result)) >= 0.8),
)

test_set_26 = (
    (([1, 1, 1, -1, -1, 1,  1, -1, 0, 0,  0],), (None)),
    (([1, 1, 1, -1, -1, 0, -1, -1, 0, 0,  0],), (None)),
    (([1, 1, 1, 1, 1, -1, 0, 0, 0, 0, 0],),     (None)),
    (([1, 1, 1,  1,  1, 1,  1,  1, 1, 0, -1],), (None)),
    (([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],),     (0)),
    (([-1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1],), (None)),
    (([1, 1, 1, 1, 1, -1, -1, 0, 0, 0, 0],),    (1)),
    (([1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],),      (0)),
    (([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],),      (1)),
    (([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],), (None)),
    (([-1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 1],), (-1)),
)



test_set_28 = (
    (('secret',), 'xjhwjy'),
    (('xyz1999',), '2346eee'),
    (('abcdef',), 'fghijk'),
    (('0123456789',), '56789abcde'),
    (('this is a string that needs to be encoded!',), 'ymnx nx f xywnsl ymfy sjjix yt gj jshtiji!'),
)


test_set_29 = (
    ((), lambda result: all(re.findall(pattern, result) for pattern in ('[0-9]', '[a-z]', '[A-Z]'))),
)


test_set_30 = (
    ((), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]),
)


test_set_103 = (
    (('WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB',), '12WB12W3B24WB'),
    (('abc',), 'abc'),
    (('abcc',), 'ab2c'),
    (('aabbbcccc',), '2a3b4c'),
    (('aa bbb cc  cc ',), '2a 3b 2c2 2c '),
    ((' ',), ' '),
    (('',), ''),
)

test_set_104 = (
    (('abc',), 'abc'),
    (('ab2c',), 'abcc'),
    (('12WB12W3B24WB',), 'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB'),
    (('2a3b4c',), 'aabbbcccc'),
    (('2a 3b 2c2 2c ',), 'aa bbb cc  cc '),
    ((' ',), ' '),
    (('',), ''),
)

test_set_105 = (
    (('8273 1232 7352 0569',), False),
    (('055-444-285',), False),
    (('4539 1488 0343 6467',), True),
    (('5169 3075 0292 3159',), True),
    (('4149 4391 0134 7643',), True),
)


test_set_106 = (
    (('sergey.brin@google.com',), 'google'),
)

test_set_107 = (
    (([2, 5, 7, 9, 11, 17, 222], 11,), 4),
    (([2, 5, 7, 9, 11, 17, 222], 42,), -1),
)

test_set_108 = (
    (([12, 24, 35, 24, 88, 120, 155, 88, 120, 155],), [12, 24, 35, 88, 120, 155]),
    (([1, 1, 1, 1, 1, 2, 1, 1, 2, 3],), [1, 2, 3]),
)


test_set_109 = (
    (([[1], [], [[[2, 3]]], [4, [5, [6]]], 7, 8],), [1, 2, 3, 4, 5, 6, 7, 8]),
    (([[1], [[[[[[[[[1]]]]]]]]], [[[2, 3]]], [4, [5, [6]]], 7, 8],), [1, 1, 2, 3, 4, 5, 6, 7, 8]),
)

test_set_110 = (
    ((0,), ()),
    ((1,), ('eggs',)),
    ((3,), ('eggs', 'peanuts')),
    ((34,), ('peanuts', 'chocolate')),
    ((42,), ('peanuts', 'strawberries', 'chocolate')),
    ((248,), ('strawberries', 'tomatoes', 'chocolate', 'pollen', 'cats')),
    ((257,), ('eggs',)),
    ((509,), ('eggs', 'shellfish', 'strawberries', 'tomatoes', 'chocolate', 'pollen', 'cats')),
)

test_set_1001 = (
    ((1, 2, 3),  49),
    ((-1, 0, 999999), 1)
)

test_set_1002 = (
    ((1, 2, 3),  -1.666666667),
    ((-1, 0, 999999), -1)
)

test_set_1003 = (
    ((1, 2, 3),  3.0),
    ((-1, 0, 999999), 4.000008000016e-06)
)

test_set_1004 = (
    ((12345,),  15),
    ((24680,), 1),
    ((11111,), 1)
)

test_set_1005 = (
    ((10, 11),  10),
    ((8, 11), 11),
    ((999999, -999999), 999999),
    ((999999, -99999), -99999)
)

test_set_1006 = (
    (('Питон', ),  True),
    (('downstream',), True),
    (('книга без слов0', ), True),
    (('изограмма', ), False)
)

test_set_1007 = (
    (('', ),  True),
)

test_set_1008 = (
    (('', ),  True),
)

test_set_1009 = (
    (('', ),  True),
)

test_set_1010 = (
    (('', ),  True),
)

test_set_1011 = (
    (('', ),  True),
)

test_set_1012 = (
    (('', ),  True),
)


#---------------------------------------------------------------
tests = {
    1: test_set_01,
    8: test_set_08,
    9: test_set_09,
    10: test_set_10,
    11: test_set_11,
    12: test_set_12,
    13: test_set_13,
    14: test_set_14,
    15: test_set_15,
    16: test_set_16,
    17: test_set_17,
    18: test_set_18,
    21: test_set_21,
    23: test_set_23,
    24: test_set_24,
    25: test_set_25,
    26: test_set_26,
    28: test_set_28,
    29: test_set_29,
    30: test_set_30,

    103: test_set_103,
    104: test_set_104,
    105: test_set_105,
    106: test_set_106,
    107: test_set_107,
    108: test_set_108,
    109: test_set_109,
    110: test_set_110,

    1001: test_set_1001,
    1002: test_set_1002,
    1003: test_set_1003,
    1004: test_set_1004,
    1005: test_set_1005,
    1006: test_set_1006,
    1007: test_set_1007,
    1008: test_set_1008,
    1009: test_set_1009,
    1010: test_set_1010,
    1011: test_set_1011,
    1012: test_set_1012,
}
