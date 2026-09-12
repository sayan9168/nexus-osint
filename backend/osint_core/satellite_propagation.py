"""Public TLE -> geodetic position propagation using SGP4."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from sgp4.api import Satrec, jday
from math import degrees, atan2, sqrt, asin

def propagate_tle(name:str,line1:str,line2:str,at:datetime|None=None)->dict[str,Any]:
    if not name or not line1 or not line2: raise ValueError("name and two TLE lines are required")
    sat=Satrec.twoline2rv(line1.strip(),line2.strip())
    when=at or datetime.now(timezone.utc)
    if when.tzinfo is None: when=when.replace(tzinfo=timezone.utc)
    jd,jdf=jday(when.year,when.month,when.day,when.hour,when.minute,when.second+when.microsecond/1e6)
    err,pos,vel=sat.sgp4(jd,jdf)
    if err: raise ValueError(f"SGP4 propagation error {err}")
    x,y,z=pos
    r=sqrt(x*x+y*y+z*z)
    lat=degrees(asin(z/r)); lon=degrees(atan2(y,x))
    return {"name":name,"latitude":lat,"longitude":lon,"altitude_km":max(0.0,r-6378.137),"velocity_km_s":sqrt(sum(v*v for v in vel)),"epoch":when.isoformat(),"source":"CelesTrak TLE / SGP4","derived":True,"note":"Position is propagated from public orbital elements, not a direct sensor observation."}
