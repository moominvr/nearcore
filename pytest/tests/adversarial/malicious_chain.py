import sys, time

sys.path.append('lib')


from cluster import start_cluster
from adversary import corrupt_node
from utils import LogTracker

TIMEOUT = 300
BLOCKS = 25
MALICIOUS_BLOCKS = 150

nodes = start_cluster(2, 1, 2, None, [["epoch_length", MALICIOUS_BLOCKS + 5], ["block_producer_kickout_threshold", 80]], {})

started = time.time()

corrupt_node(nodes[1])
tracker = LogTracker(nodes[1])

nodes[1].start(nodes[0].node_key.pk, nodes[0].addr())
time.sleep(2)
assert tracker.check("ADVERSARIAL")

print("Waiting for %s blocks..." % BLOCKS)

while True:
    assert time.time() - started < TIMEOUT
    status = nodes[1].get_status()
    height = status['sync_info']['latest_block_height']
    print(status)
    if height >= BLOCKS:
        break
    time.sleep(1)

print("Got to %s blocks, getting to fun stuff" % BLOCKS)

status = nodes[1].get_status()
print(status)

start_prod_time = time.time()
res = nodes[1].json_rpc('adv_produce_blocks', [MALICIOUS_BLOCKS, True])
assert 'result' in res, res
time.sleep(2)
status = nodes[1].get_status()
print(status)
print("Generated %s malicious blocks in %s" % (MALICIOUS_BLOCKS, time.time() - start_prod_time))

time.sleep(10)
status = nodes[0].get_status()
print(status)
height = status['sync_info']['latest_block_height']

assert height < 100

print("Epic")
