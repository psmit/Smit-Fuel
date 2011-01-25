import datetime
import fuel

def update_refueling_list():
    r0 = fuel.Refueling.all().order('odo').get()

    if r0.odo > 0:
        new_r0 = fuel.Refueling(date=datetime.datetime.combine(r0.date.date(),datetime.time(0,0,0)), odo=0, liters=0.0)
        new_r0.save()

    rest_liters = list(fuel.Refueling.all().order('odo'))
    run_restliter_algo(rest_liters)

    for rl in rest_liters: rl.save()


def run_restliter_algo(refuelings):
    def smooth_forward(refuelings,convergence_speed=0.8,tank_size = None):
        if tank_size is None:
            tank_size = max(x.liters for x in refuelings)

        start_average = _get_average(refuelings,1)
        update_low(refuelings,0,start_average,convergence_speed,tank_size)
        for i in xrange(len(refuelings)-2):
            update_high(refuelings,i,_get_average(refuelings,i+1),convergence_speed,tank_size)


    def smooth_backward(refuelings,convergence_speed=0.5,tank_size = None):
        if tank_size is None:
            tank_size = max(x.liters for x in refuelings)

        start_average = _get_average(refuelings,len(refuelings)-3)

        update_high(refuelings,len(refuelings)-2,start_average,convergence_speed + (1-convergence_speed) * 0.5 ,tank_size)

        for i in xrange(len(refuelings)-2,1,-1):
            update_low(refuelings,i,_get_average(refuelings,i-1),convergence_speed + (1-convergence_speed) * 0.5,tank_size)



    def update_high(refuelings,i,avg,convergence_speed,tank_size):
        desired_rest =  (-1.0 * avg * (refuelings[i+1].odo-refuelings[i].odo))+refuelings[i].liters+refuelings[i].rest_liters

        desired_rest = refuelings[i+1].rest_liters + (convergence_speed * (desired_rest-refuelings[i+1].rest_liters))

        refuelings[i+1].rest_liters = _get_within_bounds(0,tank_size-refuelings[i+1].liters,desired_rest)




    def update_low(refuelings,i,avg,convergence_speed,tank_size):
        desired_rest = (avg * (refuelings[i+1].odo-refuelings[i].odo))-refuelings[i].liters+refuelings[i+1].rest_liters

        desired_rest = refuelings[i].rest_liters + (convergence_speed * (desired_rest-refuelings[i].rest_liters))

        refuelings[i].rest_liters = _get_within_bounds(0,tank_size-refuelings[i].liters,desired_rest)

    def _get_average(refuelings, i):
        return (refuelings[i].liters + refuelings[i].rest_liters - refuelings[i+1].rest_liters) / (refuelings[i+1].odo - refuelings[i].odo)


    def _get_within_bounds(min_val, max_val, val):
        return float(min(max_val,max(min_val,val)))

    for i in xrange(4):
        smooth_forward(refuelings,1.0/(i+1.0))
        smooth_backward(refuelings,1.0/(i+1.0))

