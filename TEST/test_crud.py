
from memory_crud import (
    initialize_db,
    add_fact,
    get_facts,
    update_fact,
    delete_fact
)

initialize_db()

# CREATE
fact_id = add_fact("allergies", "penicillin")
print("After CREATE:", get_facts())

# UPDATE
update_fact(fact_id, "amoxicillin")
print("After UPDATE:", get_facts())

# DELETE
delete_fact(fact_id)
print("After DELETE:", get_facts())
