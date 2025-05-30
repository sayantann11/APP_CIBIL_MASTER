from flask import Flask, render_template, request, redirect, url_for, session
import requests
from flask import jsonify, make_response
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Tuple

BANK_RULES = {
    "HERO": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
        "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 14, "PASS"), (15, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "PASS"), (109, 120, "PASS"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
         "mother_0_3": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "PASS")
        ],
        "mother_4_6": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_7_12": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_13_24": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
                "mother_0_9": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ]

    },
    "IDFC": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
        "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"), (7, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 6, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 1, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "REJECT"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "REJECT"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"), (1, 1, "REJECT"), (2, 2, "REJECT"), (3, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },

    "TATA": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
        "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,9,'PASS'), (10, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 4, "PASS"), (5, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "PASS")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
                "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 0, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },

      "BAJAJ": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "REJECT"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
        "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"),(7,7,'REJECT'), (8, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "CHECK OTHER CONDITION"), (97, 108, "CHECK OTHER CONDITION"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "REJECT"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "REJECT"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
    "AXIS": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,7,'PASS'), (6, 14, "PASS"), (15, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,10,"REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
        "dpd_45_above": [
            (0, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "PASS")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(5, float('inf'), "REJECT")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(8, float('inf'), "REJECT")
        ]

    },
     "YES BANK": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"),(7,7,'REJECT'), (8, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"),(2, float('inf'), "REJECT")
        ],

        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "REJECT"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "REJECT"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "REJECT"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
     "PIRAMAL": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,7,'PASS'), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "PASS"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "PASS")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
     "HDFC": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"),(7,7,'REJECT'), (8, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 5, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "REJECT"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "REJECT"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "REJECT"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 1, "PASS"),(2, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 1, "PASS"),(2, float('inf'), "REJECT")
        ],
        "mother_0_9": [
            (0, 1, "PASS"),(2, float('inf'), "REJECT")
        ],
        "mother_0_12": [
            (0, 1, "PASS"),(2, float('inf'), "REJECT")
        ],
        "mother_0_24": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_0_60": [
            (0, 4, "PASS"),(5, float('inf'), "REJECT")
        ]
    },
    "ICICI": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "REJECT"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"),(7,7,'REJECT'), (8, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "REJECT"), (109, 120, "REJECT"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
    "POONAWALA": {
        "cibil_score": [
            (300, 650, "REJECT"), (651, 699, "REJECT"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,10,'PASS'), (11, 11, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "PASS")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_45_above": [
            (0, 1, "PASS"), (2, float('inf'), "REJECT")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "PASS"), (109, 120, "PASS"),
            (121, 132, "REJECT"), (133, 144, "REJECT"), (145, float('inf'), "REJECT")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "PASS")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 1, "PASS"),(1, float('inf'), "REJECT")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "REJECT")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "REJECT")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "REJECT")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
    "AU": {
        "cibil_score": [
            (300, 650, "PASS"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 5, "PASS"),(6,7,'PASS'), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 9, "PASS"), (10, float('inf'), "REJECT")
        ],
                "dpd_1_44": [
            (0, 0, "PASS"), (1, 9, "PASS"), (10, float('inf'), "REJECT")
        ],
        "dpd_1_above": [
            (0, 0, "PASS"), (1, 9, "PASS"), (10, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "PASS")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "PASS"), (109, 120, "PASS"),
            (121, 132, "PASS"), (133, 144, "PASS"), (145, float('inf'), "PASS")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "PASS"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "PASS")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },
    "CHOLA": {
        "cibil_score": [
            (300, 650, "PASS"), (651, 699, "PASS"), (700, 719, "PASS"),
            (720, 724, "PASS"), (725, 749, "PASS"), (750, float('inf'), "PASS")
        ],
       "cibil_enquiry_count": [
            (0, 0, "PASS"), (1, 6, "PASS"),(7,7,'REJECT'), (8, 10, "REJECT"), (11, float('inf'), "REJECT")
        ],
        "dpd_1_30": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
                "dpd_1_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
                "dpd_1_above": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, float('inf'), "REJECT")
        ],
        "dpd_31_44": [
            (0, 0, "PASS"), (1, 5, "PASS"), (6, 10, "PASS"), (11, float('inf'), "PASS")
        ],
        "dpd_45_above": [
            (0, 0, "PASS"), (1, float('inf'), "PASS")
        ],
        
        "settlements_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "settlements_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "writeoff_last_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "REJECT")
        ],
        "writeoff_older_than_24_months":[
            (-1,0,"PASS"),(1, float('inf'), "PASS")
        ],
        "car_age": [
            (0, 84, "PASS"), (85, 96, "PASS"), (97, 108, "PASS"), (109, 120, "PASS"),
            (121, 132, "PASS"), (133, 144, "PASS"), (145, float('inf'), "PASS")
        ],
        "car_owner_age": [
            (0, 21, "CHECK OTHER CONDITION"), (22, 25, "CHECK OTHER CONDITION"),
            (26, 28, "CHECK OTHER CONDITION"), (29, 30, "CHECK OTHER CONDITION"),
            (31, 53, "PASS"), (54, 70, "PASS"), (71, float('inf'), "CHECK OTHER CONDITION")
        ],
        "loan_amount": [
            (0, 100000, "PASS"), (100001, 500000, "REJECT"), (500001, float('inf'), "REJECT")
        ],
        "bounces_0_3_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, float('inf'), "REJECT")
        ],
        "bounces_0_6_months": [
            (0, 0, "PASS"), (1, 1, "PASS"), (2, 2, "PASS"), (3, 3, "PASS"), (4, float('inf'), "REJECT")
        ],
        "mother_0_3": [
            (0, 0, "PASS"),(1, float('inf'), "PASS")
        ],
        "mother_4_6": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_7_12": [
            (0, 2, "PASS"),(3, float('inf'), "PASS")
        ],
        "mother_13_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_25_60": [
            (0, 5, "PASS"),(6, float('inf'), "PASS")
        ],
        "mother_0_6": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_9": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_12": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_24": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ],
        "mother_0_60": [
            (0, 3, "PASS"),(4, float('inf'), "PASS")
        ]
    },



}


app = Flask(__name__)
app.secret_key = 'aS9!f$#3KL1sdf9asf1##2FF!' # Needed for session

@app.route('/')
def index():
    return redirect(url_for('vehicle'))



@app.route('/vehicle', methods=['GET', 'POST'])
def vehicle():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        reg_date = request.form.get('reg_date')  # May be None

        if reg_date:
            # Manual fallback
                        # Create uniform structure mimicking API format
            session['rc_data'] = {
                
                    "data": {
                        "data": {
                            "registration_date": reg_date,
                            "rc_number": vehicle_number,
                        },
                        "status_code": 200,
                        "message_code": "manual_entry",
                        "success": True
                    },
                    "message": f"Manual entry for {vehicle_number}.",
                    "source": "manual"
                
            }
            return redirect(url_for('prefill_pan'))

        # Otherwise try API
        rc_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_car"
        payload = {"id_number": vehicle_number}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(rc_api_url, json=payload, headers=headers)
            data_car = response.json()

            if response.status_code == 200 and data_car.get("status") != "error":
                session['rc_data'] = data_car
                return redirect(url_for('prefill_pan'))
            else:
                error = "Vehicle details not found. Please enter registration date manually."
                return render_template('vehicle.html', error=error, vehicle_number=vehicle_number)

        except Exception as e:
            error = f"API call failed: {str(e)}"
            return render_template('vehicle.html', error=error)

    return render_template('vehicle.html')

@app.route('/prefill_pan', methods=['GET', 'POST'])
def prefill_pan():
    if request.method == 'POST':
        mobile = request.form['mobile']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cibil_option = request.form.get('cibil_option', 'Fetch_CIBIL')
        # Step 1: PAN Prefill API
        pan_prefill_url = 'https://profilex-api.neokred.tech/core-svc/api/v2/exp/mobile-intelligence/mobile-to-pan'
        headers = {
            'client-user-id': '847ee7f5-9e05-4099-bc9e-57848d8bb77a',
            'secret-key': '64573798-eeba-47b6-b84c-405ee3636d1f',
            'access-key': '2ef62bd6-0fb7-4242-a9e1-41ed14da24e9',
            'service-id': '793c2b4d-32be-4e97-9695-beb405a0f4bf',
            'Content-Type': 'application/json'
        }
        payload = {
            "mobile": mobile,
            "firstName": first_name,
            "lastName": last_name
        }

        try:
            response = requests.post(pan_prefill_url, json=payload, headers=headers)
            
            data = response.json()
            if response.status_code == 200:
               
                pan_number = data.get('data', {}).get('pan')
            
                full_name = data.get('fullName', f"{first_name} {last_name}")
              
                gender = data.get('gender', 'Male')
                consent = 'Y'

                cibil_option = request.form.get('cibil_option', 'remote')

                if cibil_option == 'Fetch_CIBIL':
                    cibil_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_cibil"
                else:
                    print("hdkfjhdfjhafhakshf")
                    cibil_api_url = "https://api-rc-cibil-ei8h.onrender.com/overwrite_cibil"
                cibil_payload = {
                    "mobile": mobile,
                    "pan": pan_number,
                    "name": full_name,
                    "gender": gender,
                    "consent": consent
                }

                cibil_response = requests.post(cibil_api_url, json=cibil_payload, headers={'Content-Type': 'application/json'})
                cibil_data = cibil_response.json()

                if cibil_response.status_code == 200 and cibil_data.get("status") != "error":
                    session['pan_number'] = pan_number
                    session['mobile'] = mobile
                    session['name'] = full_name
                    session['gender'] = gender
                    session['consent'] = 'Y'
                    # Optionally store cibil_data too if needed
                    return redirect(url_for('analyze'))
                else:
                    error = "Neokard  API failed Mobile Number and Name doesnot match. Please enter PAN details manually."
                    form_data = {
                        "mobile": mobile,
                        "name": full_name
                    }
                    print(form_data)
                    return redirect(url_for('pan'))

            else:
                error = "PAN Prefill API failed. Please enter details manually."
                form_data = {
                    "mobile": mobile,
                    "name": f"{first_name} {last_name}"
                }
                return redirect(url_for('pan'))

        except Exception as e:
            error = f"API error: {str(e)}"
            form_data = {
                "mobile": mobile,
                "name": f"{first_name} {last_name}"
            }
            return render_template('pan.html', error=error, form_data=form_data)

    return render_template('prefill_pan.html')




@app.route('/pan', methods=['GET', 'POST'])
def pan():
    if request.method == 'POST':
        mobile = request.form['mobile']
        pan_number = request.form['pan']
        name = request.form['name']
        gender = request.form['gender']
        consent = request.form.get('consent', 'N')

        # Prepare API call
        pan_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_cibil"
        payload = {
            "mobile": mobile,
            "pan": pan_number,
            "name": name,
            "gender": gender,
            "consent": consent
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(pan_api_url, json=payload, headers=headers)
            data = response.json()
            
            if response.status_code == 200 and data.get("status") != "error":
                session['pan_number'] = pan_number
                #print("CIBIL data stored in session:", data)
                return redirect(url_for('analyze'))
            else:
                error = "CIBIL details not found. Please verify your PAN or Mobile."
                return render_template('pan.html', error=error, form_data=request.form)

        except Exception as e:
            error = f"PAN API call failed: {str(e)}"
            return render_template('pan.html', error=error, form_data=request.form)

    return render_template('pan.html', form_data={})



@app.route('/download', methods=['POST'])
def download_data():
    rc_data = session.get('rc_data')
    pan_number = session.get('pan_number')
    if not pan_number:
        return redirect(url_for('pan'))
    #print(pan_number)
    cibil_data = get_cibil_data(pan_number)
    
    if not rc_data or not cibil_data:
        return "Required data not found in session", 400

    combined_data = {
        'rc_data': rc_data,
        'cibil_data': cibil_data,
        'downloaded_at': datetime.utcnow().isoformat() + 'Z'
    }

    response = make_response(json.dumps(combined_data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=rc_cibil_data.json'
    return response
    
def get_field(field_path,data):
    current = data
    for key in field_path.split('.'):
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and key.isdigit():
            current = current[int(key)]
        else:
            return None
    return current


def count_custom_dpd_buckets(data):
    today = datetime.today()
    start_date = (today.replace(day=1) - relativedelta(months=12))
    end_date = today

    dpd_counts = {
        "dpd_1_30": 0,
        "dpd_1_45": 0,
        "dpd_1_above": 0,
        "dpd_31_44": 0,
        "dpd_45_above": 0,
    }

    for account in data.get("data", {}).get("credit_report", [])[0].get("accounts", []):
        account_type = account.get("accountType", "").lower()

        # Consider only loan-type accounts (adjust as needed)
        if "loan" not in account_type:
            continue

        for record in account.get("monthlyPayStatus", []):
            date_str = record.get("date")
            status_str = record.get("status")

            if not date_str or not status_str or status_str.lower() == "xxx":
                continue

            try:
                dpd_date = datetime.strptime(date_str, "%Y-%m-%d")
                dpd_days = int(status_str)
            except (ValueError, TypeError):
                continue

            if start_date <= dpd_date <= end_date and dpd_days > 0:
                if 1 <= dpd_days <= 30:
                    dpd_counts["dpd_1_30"] += 1
                if 1 <= dpd_days <= 45:
                    dpd_counts["dpd_1_45"] += 1
                if dpd_days >= 1:
                    dpd_counts["dpd_1_above"] += 1
                if 31 <= dpd_days <= 44:
                    dpd_counts["dpd_31_44"] += 1
                if dpd_days >= 45:
                    dpd_counts["dpd_45_above"] += 1

    return dpd_counts




def count_settlements(data):
    settlement_count = 0
    current_date = datetime.today()  # Not used in logic here but included per pattern

    accounts = data.get("data", {}).get("credit_report", [])[0].get("accounts", [])

    for account in accounts:
        try:
            wo_amount_total = float(account.get("woAmountTotal", -1))
            if wo_amount_total > 0:
                settlement_count += 1
        except (TypeError, ValueError):
            continue  # Skip invalid values

    return settlement_count



def count_bounces_by_period(data, current_date=None, exclude_account_number=None):
    if current_date is None:
        current_date = datetime.today()
    else:
        current_date = datetime.strptime(current_date, "%Y-%m-%d")

    # Prepare timeframes
    month_0_3 = current_date - relativedelta(months=3)
    month_0_6 = current_date - relativedelta(months=6)
    month_0_12 = current_date - relativedelta(months=12)

    bounces = {
        "bounces_0_3_months": 0,
        "bounces_0_6_months": 0,
        "bounces_0_12_months": 0
    }

    for account in data.get("data", {}).get("credit_report", [])[0].get("accounts", []):
        account_type = account.get("accountType", "").lower()
        account_number = account.get("accountNumber")

        if "loan" not in account_type:
            continue  # Filter only loan accounts

        # Skip the mother loan account
        if exclude_account_number and account_number == exclude_account_number:
            continue

        for record in account.get("monthlyPayStatus", []):
            date_str = record.get("date")
            status_str = record.get("status")

            if not date_str or not status_str or status_str.lower() == "xxx":
                continue

            try:
                dpd_date = datetime.strptime(date_str, "%Y-%m-%d")
                dpd = int(status_str)
            except (ValueError, TypeError):
                continue

            if dpd >= 30:
                if dpd_date >= month_0_12:
                    bounces["bounces_0_12_months"] += 1
                if dpd_date >= month_0_6:
                    bounces["bounces_0_6_months"] += 1
                if dpd_date >= month_0_3:
                    bounces["bounces_0_3_months"] += 1

    return bounces

import re

def normalize_financer_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9 ]', '', name)  # Remove punctuation
    tokens = name.split()
    blacklist = {'bank', 'limited', 'ltd', 'finserv', 'finance', 'fincorp', 'of', 'the', 'co', 'company'}
    return ' '.join([token for token in tokens if token not in blacklist])

def financer_match(financer1, financer2):
    norm1 = normalize_financer_name(financer1)
    norm2 = normalize_financer_name(financer2)
    return norm1 in norm2 or norm2 in norm1

def find_mother_auto_loan(data, data_car):
    registration_date_str = data_car["data"]["data"].get("registration_date")
    financer_name_from_rc = data_car["data"]["data"].get("financer", "")

    if not registration_date_str or not financer_name_from_rc:
        return None

    registration_date = datetime.strptime(registration_date_str, "%Y-%m-%d")
    valid_months = {
        (registration_date - relativedelta(months=i)).strftime("%Y-%m")
        for i in range(4)
    }

    accounts = data.get("data", {}).get("credit_report", [{}])[0].get("accounts", [])

    for account in accounts:
        account_type = account.get("accountType", "").lower()
        date_opened = account.get("dateOpened")
        loan_financer = account.get("memberShortName", "")

        if not date_opened or ("auto" not in account_type and "car" not in account_type):
            continue

        try:
            loan_open_month = datetime.strptime(date_opened, "%Y-%m-%d").strftime("%Y-%m")
            if loan_open_month in valid_months:
                # Enhanced financer match
                if financer_match(loan_financer, financer_name_from_rc):
                    return account
        except ValueError:
            continue

    return None

def calculate_bounce_ranges(account, as_of_date=None):
    if as_of_date is None:
        as_of_date = datetime.today()

    monthly_statuses = account.get("monthlyPayStatus", [])
    dpd_records = [
        (datetime.strptime(entry["date"], "%Y-%m-%d"), entry["status"])
        for entry in monthly_statuses
        if "status" in entry and entry["status"].isdigit() and int(entry["status"]) > 0
    ]

    # Define bucket ranges
    buckets = {
        "0_3": 3,
        "4_6": 6,
        "7_12": 12,
        "13_24": 24,
        "25_60": 60,
    }

    bounce_summary = {
        "0_3": 0, "4_6": 0, "7_12": 0, "13_24": 0, "25_60": 0,
        "0_6": 0, "0_9": 0, "0_12": 0, "0_24": 0, "0_60": 0
    }

    for dpd_date, status in dpd_records:
        month_diff = (as_of_date.year - dpd_date.year) * 12 + (as_of_date.month - dpd_date.month)

        if month_diff < 0 or month_diff > 60:
            continue

        if month_diff <= 2:
            bounce_summary["0_3"] += 1
        elif 3 <= month_diff <= 5:
            bounce_summary["4_6"] += 1
        elif 6 <= month_diff <= 11:
            bounce_summary["7_12"] += 1
        elif 12 <= month_diff <= 23:
            bounce_summary["13_24"] += 1
        elif 24 <= month_diff <= 59:
            bounce_summary["25_60"] += 1

        # Ranges
        if month_diff <= 5:
            bounce_summary["0_6"] += 1
        if month_diff <= 8:
            bounce_summary["0_9"] += 1
        if month_diff <= 11:
            bounce_summary["0_12"] += 1
        if month_diff <= 23:
            bounce_summary["0_24"] += 1
        bounce_summary["0_60"] += 1  # Always include if within 60 months

    return bounce_summary
def format_bounce_summary(bounce_summary):
    labels = {
        "0_3": "Last 0–3 months",
        "4_6": "Last 4–6 months",
        "7_12": "Last 7–12 months",
        "13_24": "Last 13–24 months",
        "25_60": "Last 25–60 months",
        "0_6": "Last 0–6 months",
        "0_9": "Last 0–9 months",
        "0_12": "Last 0–12 months",
        "0_24": "Last 0–24 months",
        "0_60": "Last 0–60 months"
    }

    formatted = {}
    for key in labels:
        count = bounce_summary.get(key, 0)
        if count > 0:
            formatted[labels[key]] = count
    return formatted


def get_cibil_data(pan):
    """Calls the /get_cibil API with the given PAN and returns the data or None."""
    try:
        response = requests.get("https://api-rc-cibil-ei8h.onrender.com/get_cibil", params={"pan": pan})
        if response.status_code == 200:
            return response.json().get("data")
        elif response.status_code == 404:
            print("No CIBIL data found.")
            return None
        else:
            print("Error fetching CIBIL data:", response.json())
            return None
    except Exception as e:
        print("Exception during API call:", str(e))
        return None

def check_condition(value, rules):
    """
    Check if a given value satisfies any of the conditions in the rules.
    """
    for rule in rules:
        min_val, max_val, result = rule
        if min_val <= value <= max_val:
            return result
    return "Invalid"
def evaluate_loan_eligibility(bank_name, cibil_score, enquiry_count, dpd_1_30, dpd_1_44,dpd_1_above, dpd_31_44, dpd_45_above,settlements_last_24_months,settlements_older_than_24_months,writeoff_last_24_months,writeoff_older_than_24_months,total_loan_amount,
                              car_age, car_owner_age, bounces_0_3, bounces_0_6,mother_0_3,mother_4_6,mother_7_12,mother_13_24,mother_25_60,mother_0_6,mother_0_9,mother_0_12,mother_0_24,mother_0_60):
    """
    Evaluate loan eligibility based on rules.
    Returns:
        - 'Eligible for Loan' if all pass
        - List of rejection reasons like 'DPD 45 Above: 2' (i.e., field: value)
    """
    bank_rules = BANK_RULES.get(bank_name)
    if not bank_rules:
        return ["Bank not supported"]
    
    checks = {
        "CIBIL Score": (cibil_score, bank_rules["cibil_score"]),
        "CIBIL Enquiry Count": (enquiry_count, bank_rules["cibil_enquiry_count"]),
        "DPD 1-30": (dpd_1_30, bank_rules["dpd_1_30"]),
        "DPD 1-44": (dpd_1_44, bank_rules["dpd_1_44"]),
        "DPD 1-Above": (dpd_1_above, bank_rules["dpd_1_above"]),
        "DPD 31-44": (dpd_31_44, bank_rules["dpd_31_44"]),
        "DPD 45 Above": (dpd_45_above, bank_rules["dpd_45_above"]),
        "Settlement last 24 months":(settlements_last_24_months,bank_rules["settlements_last_24_months"]),
        "Settlement old 24 months":(settlements_older_than_24_months,bank_rules["settlements_older_than_24_months"]),
        "Writeoff last 24 months":(writeoff_last_24_months,bank_rules["writeoff_last_24_months"]),
        "Writeoff old 24 months":(writeoff_older_than_24_months,bank_rules["writeoff_older_than_24_months"]),
        "total_loan_amount":(total_loan_amount,bank_rules["loan_amount"]),
        "Car Age": (car_age, bank_rules["car_age"]),
        "Car Owner Age": (car_owner_age, bank_rules["car_owner_age"]),
        "other Bounces 0-3 Months": (bounces_0_3, bank_rules["bounces_0_3_months"]),
        "other Bounces 0-6 Months": (bounces_0_6, bank_rules["bounces_0_6_months"]),
        "Bounces mother auto loan 0-3 months":(mother_0_3,bank_rules["mother_0_3"]),
        "Bounces mother auto loan 4-6 months":(mother_4_6,bank_rules["mother_4_6"]),
        "Bounces mother auto loan 7-12 months":(mother_7_12,bank_rules["mother_7_12"]),
        "Bounces mother auto loan 13-24 months":(mother_13_24,bank_rules["mother_13_24"]),
        "Bounces mother auto loan 25-60 months":(mother_25_60,bank_rules["mother_25_60"]),
        "Bounces mother auto loan 0-6 months":(mother_0_6,bank_rules["mother_0_6"]),
        "Bounces mother auto loan 0-9 months":(mother_0_9,bank_rules["mother_0_9"]),
        "Bounces mother auto loan 0-12 months":(mother_0_12,bank_rules["mother_0_12"]),
        "Bounces mother auto loan 0-24 months":(mother_0_24,bank_rules["mother_0_24"]),
        "Bounces mother auto loan 0-60 months":(mother_0_60,bank_rules["mother_0_60"])
            
        }

    rejection_reasons = []

    for key, (value, rule) in checks.items():
        if check_condition(value, rule) == "REJECT":
            rejection_reasons.append(f"{key}: {value}")  # Only include field and its value

    if rejection_reasons:
        return rejection_reasons
    else:
        return "Eligible for Loan"




def get_active_loan_banks(data: dict) -> list:
    """
    Extracts the bank names (memberShortName) from active non-credit-card loans.

    Args:
        data (dict): CIBIL data.

    Returns:
        list: List of bank names for active loans.
    """
    accounts = data["data"]["credit_report"][0].get("accounts", [])
    active_loan_banks = []

    for account in accounts:
        account_type = account.get("accountType", "").lower()
        if "credit card" in account_type:
            continue  # skip credit cards

        date_closed = account.get("dateClosed", "").strip().lower()
        if date_closed in ("na", "", "none"):
            bank = account.get("memberShortName", "Unknown Bank")
            active_loan_banks.append(bank)

    return active_loan_banks



from datetime import datetime
from dateutil.relativedelta import relativedelta

def count_settlements_by_age(data):
    recent_cutoff = datetime.today() - relativedelta(months=24)

    recent_settlements = 0
    old_settlements = 0

    accounts = data.get("data", {}).get("credit_report", [])[0].get("accounts", [])

    for account in accounts:
        try:
            wo_amount_total = float(account.get("woAmountTotal", -1))
            if wo_amount_total > 0:
                date_reported_str = account.get("dateReported", "")
                if date_reported_str and date_reported_str.lower() != "na":
                    date_reported = datetime.strptime(date_reported_str, "%Y-%m-%d")
                    if date_reported >= recent_cutoff:
                        recent_settlements += 1
                    else:
                        old_settlements += 1
        except (TypeError, ValueError):
            continue

    return recent_settlements, old_settlements



@app.route('/analyze')
def analyze():


    pan_number = session.get('pan_number')
    if not pan_number:
        return redirect(url_for('pan'))
    #print(pan_number)
    data = get_cibil_data(pan_number)
    
    data_car = session.get('rc_data')
    if data_car:
        rc_info = data_car.get('data', {}).get('data', {})
        owner_name = rc_info.get('owner_name', 'Not Available')
        financer_name = rc_info.get('financer', 'Not Available')
   
    
    active_loans = get_active_loan_banks(data)
    print(f"Found {len(active_loans)} active loans (non-credit-card)")

    name = get_field("data.name",data)
    credit_score = get_field("data.credit_score",data)
    print("name :",name)
    print("credit score :",credit_score)
    #Define valid enquiryPurpose codes for PL, BL, LAP, CVL
    valid_purpose_codes = {"01","05","17","32","50","51","53","54","61"}
    today = datetime.today()
    start_date = (today.replace(day=1) - relativedelta(months=3))
    enquiry_count = 0
    enquiries = data["data"]["credit_report"][0].get("enquiries", [])
    for enquiry in enquiries:
                enquiry_date_str = enquiry.get("enquiryDate")  # date format: YYYY-MM-DD
                enquiry_purpose = enquiry.get("enquiryPurpose", "")

                if enquiry_date_str and enquiry_purpose in valid_purpose_codes:
                    try:
                        enquiry_date = datetime.strptime(enquiry_date_str, "%Y-%m-%d")
                        if enquiry_date >= start_date:
                            enquiry_count += 1
                    except ValueError:
                        print(f"Invalid date format: {enquiry_date_str}")
    

    # Get the registration date from the data
    registration_date_str = data_car["data"]["data"]["registration_date"]
    registration_date = datetime.strptime(registration_date_str, "%Y-%m-%d")
    current_date = datetime.today()
    year_diff = current_date.year - registration_date.year
    month_diff = current_date.month - registration_date.month
    total_months = (year_diff * 12) + month_diff

            # Adjust if the current day is before the registration day
    if current_date.day < registration_date.day:
            total_months -= 1


    # Get the birth date from the CIBIL report
    birth_date_str = data["data"]["credit_report"][0]["names"][0]["birthDate"]
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    current_date = datetime.today()
                # Calculate age in years
    year_diff = current_date.year - birth_date.year
    month_diff = current_date.month - birth_date.month
    day_diff = current_date.day - birth_date.day
    # Adjust if birthday hasn't occurred this year
    if month_diff < 0 or (month_diff == 0 and day_diff < 0):
        year_diff -= 1
    

    

    # Define keywords to identify relevant loan types
    keywords = ["personal", "business"]

    # Get the accounts list
    accounts = data["data"]["credit_report"][0]["accounts"]

    # Get today's date
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month

    # Initialize highest loan amount
    total_loan_amount = 0

    # Loop through each account
    for account in accounts:
        account_type = account.get("accountType", "").lower()
        if any(keyword in account_type for keyword in keywords):
            monthly_status = account.get("monthlyPayStatus", [])
            
            # Check latest funding condition (less than 3 months of data)
            if len(monthly_status) <= 3:
                # Parse dateOpened
                
                try:
                    date_opened = datetime.strptime(account.get("dateOpened", ""), "%Y-%m-%d")

                    # Calculate month difference (treat current month as 0)
                    month_diff = (current_year - date_opened.year) * 12 + (current_month - date_opened.month)
                    print("month_diff",month_diff)
                    # Only consider loans opened in last 5 months (0 to 4)
                    if 0 <= month_diff < 5:
                        loan_amount = int(account.get("highCreditAmount", 0))
                        print("loan amount",loan_amount)
                        total_loan_amount = total_loan_amount+loan_amount
                except (ValueError, TypeError):
                    continue  # skip invalid dates

    print(f"Highest recent latest-funded loan amount (0–4 months): {total_loan_amount}")



    

    # Example usage
    dpd_summary = count_custom_dpd_buckets(data)
    
    print("=================================")
    mother_loan = find_mother_auto_loan(data, data_car)
    print(mother_loan)
    print("=================================")
    current_date = datetime.today().strftime("%Y-%m-%d")
    exclude_account_number = mother_loan.get("accountNumber") if mother_loan else None

    bounces = count_bounces_by_period(data, current_date=current_date, exclude_account_number=exclude_account_number)
    # Store individual values from summary dictionary into variables
    dpd_1_30_count = dpd_summary.get("dpd_1_30", 0)
    dpd_1_45_count = dpd_summary.get("dpd_1_45", 0)
    dpd_1_above = dpd_summary.get("dpd_1_above", 0)
    dpd_31_44_count = dpd_summary.get("dpd_31_44", 0)
    dpd_45_above = dpd_summary.get("dpd_45_above", 0)
    bounce_0_3 = bounces["bounces_0_3_months"]
    bounces_0_6 =  bounces["bounces_0_6_months"]
    
    print("##############################")
    print("Valid PL/BL/LAP/CVL enquiries in current + last 3 calendar months:", enquiry_count)
    print(f"Total loan amount: {total_loan_amount}")
    print(f"Car Age in months: {total_months}")
    print(f"Car Owner Age (based on CIBIL birthDate): {year_diff} years")
    print("Custom DPD Summary in Last 12 Months:", dpd_summary)
    print("Bounce Summary:")
    print(bounces)
    print("dpd 1-30",dpd_1_30_count)
    print("dpd 1-45",dpd_1_45_count)
    print("dpd 1 and above",dpd_1_above)
    print("dpd 31-45",dpd_31_44_count)
    print("dpd 45 and above",dpd_45_above)
    
    recent_settlements, old_settlements = count_settlements_by_age(data)

    # Store in separate variables
    settlements_last_24_months = recent_settlements
    settlements_older_than_24_months = old_settlements
    writeoff_last_24_months = recent_settlements
    writeoff_older_than_24_months = old_settlements
    # Print for confirmation
    print("Settlements in the last 24 months:", settlements_last_24_months)
    print("Settlements older than 24 months:", settlements_older_than_24_months)
    print("Settlements older than 24 months:", writeoff_last_24_months)
    print("Settlements in the last 24 months:", writeoff_older_than_24_months)
    mother_0_3 =    0
    mother_4_6 =0
    mother_7_12 = 0
    mother_13_24 = 0
    mother_25_60 = 0
    mother_0_6 =0
    mother_0_9 =0
    mother_0_12 = 0
    mother_0_24 = 0
    mother_0_60 = 0
    if mother_loan:
        bounces = calculate_bounce_ranges(mother_loan)
        print("✅ Mother Loan Found")
        print("Account Number:", mother_loan["accountNumber"])
        print("Bank:", mother_loan.get("memberShortName", "Unknown"))
        print("Loan Opened On:", mother_loan.get("dateOpened", "N/A"))
        print(format_bounce_summary(bounces))
        mother_0_3 = bounces["0_3"]
        mother_4_6 = bounces["4_6"]
        mother_7_12 = bounces["7_12"]
        mother_13_24 = bounces["13_24"]
        mother_25_60 = bounces["25_60"]
        mother_0_6 = bounces["0_6"]
        mother_0_9 = bounces["0_9"]
        mother_0_12 = bounces["0_12"]
        mother_0_24 = bounces["0_24"]
        mother_0_60 = bounces["0_60"]
    else:
        print("❌ No matching Auto/Car loan found.")
        
    banks = ['HERO', 'TATA', 'BAJAJ','IDFC', 'YES BANK', 'PIRAMAL', 'HDFC', 'ICICI', 'POONAWALA', 'AU', 'CHOLA','AXIS']
    accepted_banks = []
    rejected_banks = {}
    for bank in banks:
        result = evaluate_loan_eligibility(
            bank, 
            int(credit_score), 
            int(enquiry_count), 
            int(dpd_1_30_count), 
            int(dpd_1_45_count),
            int(dpd_1_above),
            int(dpd_31_44_count),
            int(dpd_45_above),
            int(settlements_last_24_months),
            int(settlements_older_than_24_months),
            int(writeoff_last_24_months),
            int(writeoff_older_than_24_months),
            int(total_loan_amount),
            int(total_months), 
            int(year_diff), 
            int(bounce_0_3), 
            int(bounces_0_6),
            int(mother_0_3),
            int(mother_4_6),
            int(mother_7_12),
            int(mother_13_24),
            int(mother_25_60),
            int(mother_0_6),
            int(mother_0_9),
            int(mother_0_12),
            int(mother_0_24),
            int(mother_0_60)
        )
    
        if result == "Eligible for Loan":
            accepted_banks.append(bank)
        else:
            rejected_banks[bank] = result  # Store rejection reason
    
    
    bounce_summary = format_bounce_summary(bounces)
    
    eligibility_result =1
    # Safely pass the data to the template
    return render_template('analyze.html', result=eligibility_result, rc_data=data_car or {}, cibil_data=data or {},accepted_banks=accepted_banks,rejected_banks=rejected_banks,mother_loan=mother_loan or {},bounce_summary=bounce_summary or {},pan_number=pan_number,name=name,active_loans=active_loans,owner_name=owner_name,financer_name=financer_name,credit_score=credit_score)



def process_eligibility(pan_number, vehicle_data,reg_date=None):
    data = get_cibil_data(pan_number)

    if reg_date:
        print("case1####")
        # Construct data_car in the same structure as API response
        data_car = {
            "data": {
                "data": {
                    "registration_date": reg_date,
                    "owner_name": "Not Available",
                    "financer": "Not Available"
                }
            }
        }
    else:
        print("case2 ###############################")
        rc_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_car"
        payload = {"id_number": vehicle_data}
        headers = {"Content-Type": "application/json"}
        response = requests.post(rc_api_url, json=payload, headers=headers)
        data_car = response.json()
    if data_car:
        rc_info = data_car.get('data', {}).get('data', {})
        owner_name = rc_info.get('owner_name', 'Not Available')
        financer_name = rc_info.get('financer', 'Not Available')
   
    
    active_loans = get_active_loan_banks(data)
    print(f"Found {len(active_loans)} active loans (non-credit-card)")
    name = get_field("data.name",data)
    credit_score = get_field("data.credit_score",data)
    print("name :",name)
    print("credit score :",credit_score)
    #Define valid enquiryPurpose codes for PL, BL, LAP, CVL
    valid_purpose_codes = {"01","05","17","32","50","51","53","54","61"}
    today = datetime.today()
    start_date = (today.replace(day=1) - relativedelta(months=3))
    enquiry_count = 0
    enquiries = data["data"]["credit_report"][0].get("enquiries", [])
    for enquiry in enquiries:
                enquiry_date_str = enquiry.get("enquiryDate")  # date format: YYYY-MM-DD
                enquiry_purpose = enquiry.get("enquiryPurpose", "")

                if enquiry_date_str and enquiry_purpose in valid_purpose_codes:
                    try:
                        enquiry_date = datetime.strptime(enquiry_date_str, "%Y-%m-%d")
                        if enquiry_date >= start_date:
                            enquiry_count += 1
                    except ValueError:
                        print(f"Invalid date format: {enquiry_date_str}")
    

    # Get the registration date from the data
    registration_date_str = data_car["data"]["data"]["registration_date"]
    registration_date = datetime.strptime(registration_date_str, "%Y-%m-%d")
    current_date = datetime.today()
    year_diff = current_date.year - registration_date.year
    month_diff = current_date.month - registration_date.month
    total_months = (year_diff * 12) + month_diff

            # Adjust if the current day is before the registration day
    if current_date.day < registration_date.day:
            total_months -= 1


    # Get the birth date from the CIBIL report
    birth_date_str = data["data"]["credit_report"][0]["names"][0]["birthDate"]
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    current_date = datetime.today()
                # Calculate age in years
    year_diff = current_date.year - birth_date.year
    month_diff = current_date.month - birth_date.month
    day_diff = current_date.day - birth_date.day
    # Adjust if birthday hasn't occurred this year
    if month_diff < 0 or (month_diff == 0 and day_diff < 0):
        year_diff -= 1
    

    

    # Define keywords to identify relevant loan types
    keywords = ["personal", "business"]

    # Get the accounts list
    accounts = data["data"]["credit_report"][0]["accounts"]

    # Get today's date
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month

    # Initialize highest loan amount
    total_loan_amount = 0

    # Loop through each account
    for account in accounts:
        account_type = account.get("accountType", "").lower()
        if any(keyword in account_type for keyword in keywords):
            monthly_status = account.get("monthlyPayStatus", [])
            
            # Check latest funding condition (less than 3 months of data)
            if len(monthly_status) <= 3:
                # Parse dateOpened
                
                try:
                    date_opened = datetime.strptime(account.get("dateOpened", ""), "%Y-%m-%d")

                    # Calculate month difference (treat current month as 0)
                    month_diff = (current_year - date_opened.year) * 12 + (current_month - date_opened.month)
                    print("month_diff",month_diff)
                    # Only consider loans opened in last 5 months (0 to 4)
                    if 0 <= month_diff < 5:
                        loan_amount = int(account.get("highCreditAmount", 0))
                        print("loan amount",loan_amount)
                        total_loan_amount = total_loan_amount+loan_amount
                except (ValueError, TypeError):
                    continue  # skip invalid dates

    print(f"Highest recent latest-funded loan amount (0–4 months): {total_loan_amount}")



    

    # Example usage
    dpd_summary = count_custom_dpd_buckets(data)
    
    
    mother_loan = find_mother_auto_loan(data, data_car)
    print(mother_loan)
   
    current_date = datetime.today().strftime("%Y-%m-%d")
    exclude_account_number = mother_loan.get("accountNumber") if mother_loan else None

    bounces = count_bounces_by_period(data, current_date=current_date, exclude_account_number=exclude_account_number)
    # Store individual values from summary dictionary into variables
    dpd_1_30_count = dpd_summary.get("dpd_1_30", 0)
    dpd_1_45_count = dpd_summary.get("dpd_1_45", 0)
    dpd_1_above = dpd_summary.get("dpd_1_above", 0)
    dpd_31_44_count = dpd_summary.get("dpd_31_44", 0)
    dpd_45_above = dpd_summary.get("dpd_45_above", 0)
    bounce_0_3 = bounces["bounces_0_3_months"]
    bounces_0_6 =  bounces["bounces_0_6_months"]
    
    print("##############################")
    print("Valid PL/BL/LAP/CVL enquiries in current + last 3 calendar months:", enquiry_count)
    print(f"Total loan amount: {total_loan_amount}")
    print(f"Car Age in months: {total_months}")
    print(f"Car Owner Age (based on CIBIL birthDate): {year_diff} years")
    print("Custom DPD Summary in Last 12 Months:", dpd_summary)
    print("Bounce Summary:")
    print(bounces)
    print("dpd 1-30",dpd_1_30_count)
    print("dpd 1-45",dpd_1_45_count)
    print("dpd 1 and above",dpd_1_above)
    print("dpd 31-45",dpd_31_44_count)
    print("dpd 45 and above",dpd_45_above)
    
     #calculation of mother auto loan
    recent_settlements, old_settlements = count_settlements_by_age(data)

    # Store in separate variables
    settlements_last_24_months = recent_settlements
    settlements_older_than_24_months = old_settlements
    writeoff_last_24_months = recent_settlements
    writeoff_older_than_24_months = old_settlements
    # Print for confirmation
    print("Settlements in the last 24 months:", settlements_last_24_months)
    print("Settlements older than 24 months:", settlements_older_than_24_months)
    print("Settlements older than 24 months:", writeoff_last_24_months)
    print("Settlements in the last 24 months:", writeoff_older_than_24_months)
    mother_0_3 =    0
    mother_4_6 =0
    mother_7_12 = 0
    mother_13_24 = 0
    mother_25_60 = 0
    mother_0_6 =0
    mother_0_9 =0
    mother_0_12 = 0
    mother_0_24 = 0
    mother_0_60 = 0
    if mother_loan:
        bounces = calculate_bounce_ranges(mother_loan)
        print("✅ Mother Loan Found")
        print("Account Number:", mother_loan["accountNumber"])
        print("Bank:", mother_loan.get("memberShortName", "Unknown"))
        print("Loan Opened On:", mother_loan.get("dateOpened", "N/A"))
        print(format_bounce_summary(bounces))
        mother_0_3 = bounces["0_3"]
        mother_4_6 = bounces["4_6"]
        mother_7_12 = bounces["7_12"]
        mother_13_24 = bounces["13_24"]
        mother_25_60 = bounces["25_60"]
        mother_0_6 = bounces["0_6"]
        mother_0_9 = bounces["0_9"]
        mother_0_12 = bounces["0_12"]
        mother_0_24 = bounces["0_24"]
        mother_0_60 = bounces["0_60"]
    else:
        print("❌ No matching Auto/Car loan found.")
        
    banks = ['HERO', 'TATA', 'BAJAJ','IDFC', 'YES BANK', 'PIRAMAL', 'HDFC', 'ICICI', 'POONAWALA', 'AU', 'CHOLA','AXIS']
    accepted_banks = []
    rejected_banks = {}
    for bank in banks:
        result = evaluate_loan_eligibility(
            bank, 
            int(credit_score), 
            int(enquiry_count), 
            int(dpd_1_30_count), 
            int(dpd_1_45_count),
            int(dpd_1_above),
            int(dpd_31_44_count),
            int(dpd_45_above),
            int(settlements_last_24_months),
            int(settlements_older_than_24_months),
            int(writeoff_last_24_months),
            int(writeoff_older_than_24_months),
            int(total_loan_amount),
            int(total_months), 
            int(year_diff), 
            int(bounce_0_3), 
            int(bounces_0_6),
            int(mother_0_3),
            int(mother_4_6),
            int(mother_7_12),
            int(mother_13_24),
            int(mother_25_60),
            int(mother_0_6),
            int(mother_0_9),
            int(mother_0_12),
            int(mother_0_24),
            int(mother_0_60)
        )
    
        if result == "Eligible for Loan":
            accepted_banks.append(bank)
        else:
            rejected_banks[bank] = result  # Store rejection reason
    
    
    bounce_summary = format_bounce_summary(bounces)
    
    eligibility_result =1        
    
    print(mother_loan)
    return {
        "eligibility_result": 1,
        "7accepted_banks": accepted_banks,
        "8rejected_banks": rejected_banks,
        "3bounce_summary": bounce_summary,
        "2pan_number": pan_number,
        "1name": name,
        "4owner_name": owner_name,
        "5financer_name": financer_name,
        "6active_loans": active_loans,
        "9mother_loan": mother_loan or {},
        "rc_data": data_car or {},
        "cibil_data": data or {},
        "3credit_score": credit_score
    }



@app.route('/api/output', methods=['POST'])
def output():
    payload = request.json
    vehicle_number = payload.get('vehicle_number')
    phone_number = payload.get('phone_number')
    first_name = payload.get('first_name')
    last_name = payload.get('last_name')

    #rc_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_car"
    headers_json = {"Content-Type": "application/json"}
    #rc_payload = {"id_number": vehicle_number}

    try:
        # Step 1: Vehicle RC API
        #response = requests.post(rc_api_url, json=rc_payload, headers=headers_json)
        #data_car = response.json()
#
        #if response.status_code != 200 or data_car.get("status") == "error":
        #    return jsonify({"error": "Vehicle details not found. Please enter registration date manually."}), 400

        # Step 2: PAN Prefill API
        pan_prefill_url = 'https://profilex-api.neokred.tech/core-svc/api/v2/exp/mobile-intelligence/mobile-to-pan'
        pan_headers = {
            'client-user-id': '847ee7f5-9e05-4099-bc9e-57848d8bb77a',
            'secret-key': '64573798-eeba-47b6-b84c-405ee3636d1f',
            'access-key': '2ef62bd6-0fb7-4242-a9e1-41ed14da24e9',
            'service-id': '793c2b4d-32be-4e97-9695-beb405a0f4bf',
            'Content-Type': 'application/json'
        }
        pan_payload = {
            "mobile": phone_number,
            "firstName": first_name,
            "lastName": last_name
        }

        response = requests.post(pan_prefill_url, json=pan_payload, headers=pan_headers)
        data = response.json()

        if response.status_code == 200:
            pan_number = data.get('data', {}).get('pan')
            #print(pan_number)
            if not pan_number:
                return jsonify({"error": "Missing PAN  NEOKRED SHOW SUCESS but no PAN RETURNED"}), 400

            full_name = data.get('fullName', f"{first_name} {last_name}")
            gender = data.get('gender', 'Male')
            consent = 'Y'

            # Step 3: CIBIL API
            cibil_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_cibil"
            cibil_payload = {
                "mobile": phone_number,
                "pan": pan_number,
                "name": full_name,
                "gender": gender,
                "consent": consent
            }

            cibil_response = requests.post(cibil_api_url, json=cibil_payload, headers=headers_json)
            cibil_data = cibil_response.json()
            if cibil_response.status_code != 200 or cibil_data.get("status") == "error":
                return jsonify({
                    "error": "CIBIL API request failed"
                }), 400
            if not vehicle_number:
                return jsonify({"error": "RC data"}), 400
            
            
            
            result = process_eligibility(pan_number, vehicle_number)
            return jsonify(result), 200
            
           

        else:
            return jsonify({"error": "NEOKRED API FAIL Please enter PAN details manually."}), 400

    except Exception as e:
        return jsonify({"error": f"CAR API call failed: {str(e)}"}), 500
            
    
@app.route('/api/outputnorc', methods=['POST'])
def output_norc():
    payload = request.json
    vehicle_number = payload.get('vehicle_number')
    phone_number = payload.get('phone_number')
    first_name = payload.get('first_name')
    last_name = payload.get('last_name')
    reg_date = payload.get("reg_date")

    #rc_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_car"
    headers_json = {"Content-Type": "application/json"}
    #rc_payload = {"id_number": vehicle_number}

    try:
        # Step 1: Vehicle RC API
        #response = requests.post(rc_api_url, json=rc_payload, headers=headers_json)
        #data_car = response.json()
#
        #if response.status_code != 200 or data_car.get("status") == "error":
        #    return jsonify({"error": "Vehicle details not found. Please enter registration date manually."}), 400

        # Step 2: PAN Prefill API
        pan_prefill_url = 'https://profilex-api.neokred.tech/core-svc/api/v2/exp/mobile-intelligence/mobile-to-pan'
        pan_headers = {
            'client-user-id': '847ee7f5-9e05-4099-bc9e-57848d8bb77a',
            'secret-key': '64573798-eeba-47b6-b84c-405ee3636d1f',
            'access-key': '2ef62bd6-0fb7-4242-a9e1-41ed14da24e9',
            'service-id': '793c2b4d-32be-4e97-9695-beb405a0f4bf',
            'Content-Type': 'application/json'
        }
        pan_payload = {
            "mobile": phone_number,
            "firstName": first_name,
            "lastName": last_name
        }

        response = requests.post(pan_prefill_url, json=pan_payload, headers=pan_headers)
        data = response.json()

        if response.status_code == 200:
            pan_number = data.get('data', {}).get('pan')
            print(pan_number)
            full_name = data.get('fullName', f"{first_name} {last_name}")
            gender = data.get('gender', 'Male')
            consent = 'Y'

            # Step 3: CIBIL API
            cibil_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_cibil"
            cibil_payload = {
                "mobile": phone_number,
                "pan": pan_number,
                "name": full_name,
                "gender": gender,
                "consent": consent
            }

            cibil_response = requests.post(cibil_api_url, json=cibil_payload, headers=headers_json)
            cibil_data = cibil_response.json()
            if cibil_response.status_code != 200 or cibil_data.get("status") == "error":
                return jsonify({
                    "error": "CIBIL API request failed"
                }), 400
            if not pan_number or not vehicle_number:
                return jsonify({"error": "Missing PAN or RC data"}), 400
            
            
            
            result = process_eligibility(pan_number, vehicle_number,reg_date=reg_date)
            return jsonify(result), 200
            
           

        else:
            return jsonify({"error": "NEOKRED API FAIL Please enter PAN details manually."}), 400

    except Exception as e:
        return jsonify({"error": f"outputnorc CAR API call failed: {str(e)}"}), 500
    







@app.route('/api/outputnopan', methods=['POST'])
def output_nopan():
    try:
        payload = request.json

        # Extract required fields
        vehicle_number = payload.get('vehicle_number')
        phone_number = payload.get('phone_number')
        first_name = payload.get('first_name')
        last_name = payload.get('last_name')
        pan_number = payload.get('pan')
        gender = payload.get('gender', 'M')  # defaulting to 'M' if not provided
        # optional or to be derived elsewhere

        # Validate required fields
        if not all([vehicle_number, phone_number, first_name, last_name, pan_number]):
            return jsonify({"error": "Missing required fields"}), 400

        full_name = f"{first_name} {last_name}"
        consent = 'Y'

        # CIBIL API call
        cibil_api_url = "https://api-rc-cibil-ei8h.onrender.com/fetch_cibil"
        headers_json = {"Content-Type": "application/json"}
        cibil_payload = {
            "mobile": phone_number,
            "pan": pan_number,
            "name": full_name,
            "gender": gender,
            "consent": consent
        }

        cibil_response = requests.post(cibil_api_url, json=cibil_payload, headers=headers_json)

        if cibil_response.status_code != 200:
            return jsonify({"error": "CIBIL API request failed"}), 400

        cibil_data = cibil_response.json()
        if cibil_data.get("status") == "error":
            return jsonify({"error": "CIBIL API returned error"}), 400

        # Ensure reg_date is available for process_eligibility


        # Final processing (Assuming process_eligibility is defined elsewhere)
        result = process_eligibility(pan_number, vehicle_number)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"outputnopan API call failed: {str(e)}"}), 500










@app.route('/api/analyze', methods=['POST'])
def analyze_api():
    payload = request.json
    pan_number = payload.get('pan_number')
    vehicle_number = payload.get('vehicle_number')

    if not pan_number or not vehicle_number:
        return jsonify({"error": "Missing PAN or RC data"}), 400
    
    try:
        result = process_eligibility(pan_number, vehicle_number)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
