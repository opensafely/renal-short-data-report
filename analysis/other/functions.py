 def make_measure(numer, grp):
        return {
             Measure(
            id=f"{numer}_{grp}",
            numerator=numer,
            denominator="population",
            group_by=[grp],
            small_number_suppression=False
             )
        }