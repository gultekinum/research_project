import random
from random import randint
import sys

party_list =["A Party","B Party","C Party","D Party"]

def prepare_vote_data(person_count):
    
    person_list = []
    for i in range(person_count):
        num = randint(10000000000,99999999999)
        party = random.choice(party_list)
        while num in person_list:
            num = random.randint(10000000000,99999999999)
            party = random.choice(party_list)
        person_list.append("{}:{}".format(str(num),party))
    f = open("vote_list.txt","w")
    f.write("\n".join(person_list))


prepare_vote_data(int(sys.argv[1]))




    