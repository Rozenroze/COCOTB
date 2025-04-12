database -open waves -into waves.shm -default -compress
probe -database waves -all -memories -depth all -packed 100000
run
exit