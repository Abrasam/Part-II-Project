from tests.test_kbucket import *
from tests.test_routingtable import *
from tests.test_storage import *

print("Testing KBucket...", end=" ")
test_kbucket()
print("Passed")
print("Testing Storage...", end=" ")
test_store()
test_iter()
print("Passed")
print("Testing Routing Table...", end=" ")
test_table_contacts()
print("Passed")