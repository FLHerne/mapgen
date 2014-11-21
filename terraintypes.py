import json
import numpy


def conditionMap(in_map, out_map, value, **conditions):
    """Set out_map to value where in_map is True and all conditions are met"""
    ml = [in_map]  # Nasty hack because nonlocal is python3 only.
    assert in_map.shape == out_map.shape

    def checkRequirement(check_map, requirelist):
        """Test if checkmap values are in requirelist"""
        fits = numpy.zeros(check_map.shape, dtype=numpy.bool_)
        for required in requirelist:
            fits |= (out_map == required)
        ml[0] &= fits

    if 'require' in conditions:
        checkRequirement(out_map, conditions['require'])
    if 'avoid' in conditions:
        for avoided in conditions['avoid']:
            in_map &= (out_map != avoided)
    if 'req_omap' in conditions:
        for omap, requirelist in conditions['req_omap']:
            checkRequirement(omap, requirelist)

    out_map[in_map] = value
