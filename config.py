#config constants
class cow_sim_config:
	#price cons
	price_per_kg_normal = 53000
	price_of_concentraat = 3200
	price_per_cow_250kg = 12500000
	price_of_grass = 500
	price_fermented_poop = 1200
	price_per_kg_eid = 6000
	price_of_concentraat_if_gt_100_decrease = 10

	#fin cons
	my_share_low = 60.00
	my_share_high = 70.00

	#cattle cons
	monthly_targeted_adg_kg_per_cattle = 30
	cattle_bought_at_kg = 250
	amount_max_capacity = 1000
	amount_change_to_cycle_strat = 1001

	#labor cons
	cost_of_farmhand = 2500000
	cost_of_security_guard = 2500000

	#sim cons
	cycle_length = 3

	#feed cons
	percentage_of_dry_matter = 2.7
	percentage_of_dry_matter_concentraat = 60
	percentage_of_concentraat_dry = 80
	percentage_of_dry_matter_grass = 40
	percentage_of_grass_dry = 20

	#poop cons
	percentage_poop_dry = 25
	percentage_poop_fermented_weight_decrease = 50
	
	bool_financials = True

#finance config
percentage_own = 60
money_invested = 150000000
