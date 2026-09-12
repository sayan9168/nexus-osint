from osint_core.nextgen_intelligence import correlate_signals,density_heatmap,fuse_timeline
from osint_core.satellite_propagation import propagate_tle

def test_correlation_and_density():
 signals=[{"id":"a","lat":10.1,"lon":20.2,"confidence":.9,"source":"A"},{"id":"b","lat":10.3,"lon":20.4,"confidence":.7,"source":"B"}]
 assert correlate_signals(signals)["cluster_count"]==1
 assert density_heatmap(signals)["cells"][0]["count"]==2

def test_timeline_sorted():
 rows=fuse_timeline([{ "observed_at":"2026-01-02T00:00:00Z","source":"case"},{"observed_at":"2026-01-01T00:00:00Z","source":"case"}],[])
 assert rows[0]["timestamp"].startswith("2026-01-01")

def test_tle_propagation():
 result=propagate_tle("ISS","1 25544U 98067A   24180.00000000  .00010000  00000-0  18000-3 0  9999","2 25544  51.6400 120.0000 0005000  40.0000  80.0000 15.50000000123456")
 assert -90 <= result["latitude"] <= 90
 assert -180 <= result["longitude"] <= 180
 assert result["derived"] is True
