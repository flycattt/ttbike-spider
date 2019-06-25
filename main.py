from ttbikeSpider import ttbikeSpider

ttbike=ttbikeSpider(token="",
	path=os.getcwd(),
	city="南京市",
	cityCode="025",
	adCode="320100",
	timeout=6,
	nums=2
	)
ttbike.run(118.90341,32.100929,118.93541,32.108229)