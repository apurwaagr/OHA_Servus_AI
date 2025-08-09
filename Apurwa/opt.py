#!/usr/bin/env python3
"""
Advanced Neumarkt Bus Route Optimizer
Complete Before/After Analysis with Smart Recommendations
"""

import csv
import json
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class RouteMetrics:
    passengers_per_day: float
    efficiency_score: float
    cost_per_passenger: float
    occupancy_rate: float
    revenue_potential: float

@dataclass
class ScheduleComparison:
    before_frequency: int
    after_frequency: int
    before_trips_per_day: int
    after_trips_per_day: int
    frequency_change_percent: float
    cost_impact: float

class BusStop:
    def __init__(self, name, passengers_weekday, passengers_total, route_numbers):
        self.name = name
        self.passengers_weekday = passengers_weekday
        self.passengers_total = passengers_total
        self.route_numbers = route_numbers
        self.priority = self._calculate_priority()
        self.zone = self._determine_zone()
        self.demand_pattern = self._analyze_demand_pattern()
        
    def _calculate_priority(self):
        if self.passengers_total > 100:
            return "critical"
        elif self.passengers_total > 50:
            return "high"
        elif self.passengers_total > 20:
            return "medium"
        else:
            return "low"
    
    def _determine_zone(self):
        core_keywords = ["bahnhof", "markt", "rathaus", "zentrum", "klinikum", "landratsamt"]
        suburban_keywords = ["schule", "kirche", "friedhof", "str.", "weg", "platz"]
        remote_keywords = ["mühle", "hof", "berg", "tal", "dorf"]
        
        name_lower = self.name.lower()
        if any(keyword in name_lower for keyword in core_keywords):
            return "core"
        elif any(keyword in name_lower for keyword in remote_keywords):
            return "remote"
        else:
            return "suburban"
    
    def _analyze_demand_pattern(self):
        weekday_ratio = self.passengers_weekday / self.passengers_total if self.passengers_total > 0 else 0
        if weekday_ratio > 0.8:
            return "business_focused"
        elif weekday_ratio > 0.6:
            return "mixed_use"
        else:
            return "leisure_focused"

class SmartBusOptimizer:
    def __init__(self):
        self.stops = []
        self.routes = defaultdict(list)
        self.current_schedules = {}
        self.optimized_schedules = {}
        self.route_metrics = {}
        self.recommendations = []
        self.parse_real_data()
        self._initialize_current_schedules()
    
    def parse_real_data(self):
        """Parse the comprehensive passenger data"""
        # Using the full dataset from your provided file
        raw_data = """561	Neumarkt Bahnhof	111.0	775.6
561	Oberer Markt	62.5	178.0
561	Rathaus	56.3	158.9
561	Landratsamt	63.3	104.4
561	Ahntweg	8.7	8.7
561	Bergstr. (Pölling)	16.3	16.3
561	Fliederweg	18.3	18.3
561	Flugplatz	8.8	8.8
561	Gasthof Feihl (Pölling)	50.6	50.6
561	Johanneszentrum	1.7	18.1
561	Kapellenweg (Rittershof)	13.0	13.0
561	Klinikum	34.8	60.4
561	Kreuzstr.	0.1	11.0
561	Marienbader Str.	4.7	4.7
561	Meuselstr.	3.2	11.2
561	Nibelungenstr.	4.9	4.9
561	Nürnberger Str.	35.5	35.5
561	Pöllinger Höhe	3.4	3.4
561	Siedlerstr. (Pölling)	15.1	15.1
561	Siegfriedstr. (Pölling)	5.7	5.7
561	Stadtweg (Pölling)	10.7	10.7
561	Volksfestplatz	4.5	30.4
561	Woffenbacher Str.	0.4	5.9
562	Neumarkt Bahnhof	0.0	71.9
562	Oberer Markt	0.0	28.7
562	Rathaus	0.0	18.7
562	Landratsamt	0.0	41.1
562	Am Sand	1.9	1.9
562	Heiligenwiesen	7.5	7.5
562	Holzheim Schule	11.6	11.6
562	Klinikum	0.0	25.6
562	Maienbreite	16.2	16.3
562	St.-Anna-Str.	6.7	6.7
562	Triftstr.	1.2	1.2
563	Neumarkt Bahnhof	0.0	97.7
563	Oberer Markt	0.0	59.2
563	Rathaus	0.0	45.8
563	Altdorfer Str.	2.0	2.5
563	Altenhof Geschäftszentrum	21.9	23.2
563	Altenhofweg	11.7	11.7
563	Am Evangelienstein	7.1	7.1
563	Breslauer Str.	8.2	8.2
563	Eichendorffstr.	4.7	4.7
563	Hermann-Stehr-Str.	18.7	18.7
563	Johann-Mois-Ring	9.1	9.8
563	Johanneszentrum	0.0	1.8
563	Kornstr.	16.8	16.8
563	Koppenmühlweg	8.4	8.4
563	Landesgartenschau	17.2	19.0
563	Milchhofstr.	0.0	0.6
563	Neuer Markt	38.2	40.4
564	Neumarkt Bahnhof	0.0	59.7
564	Abzw. Regerstr.	3.0	3.0
564	Amberger Str.	0.1	0.1
564	EFA-Str.	3.6	3.6
564	Faberpark	0.2	0.2
564	Heideweg	10.6	10.6
564	Kapuzinerhölzl	5.8	5.8
564	Karl-Speier-Str.	11.9	26.1
564	Klostertor	6.1	11.1
564	Kohlenbrunnermühlstr.	8.1	8.1
564	Leipzigerstr.	6.3	6.3
564	Museum Lothar Fischer	29.4	47.9
564	Pelchenhofener Str.	5.8	5.8
564	Pulveräcker	0.4	0.4
564	Regerstr.	3.5	3.5
564	Sachsenstr.	4.9	4.9
564	Schafhof	1.2	1.2
564	Schillerstr.	5.0	5.0
564	Schlossbad	25.2	41.0
564	Theo-Betz-Platz	23.4	143.0
564	Wilhelm-Busch-Str.	5.2	5.2
565	Neumarkt Bahnhof	0.0	81.2
565	Am Lohgraben	11.9	11.9
565	Birkenweg	7.7	7.7
565	Egerländer Str.	5.5	5.5
565	Föhrenweg	11.2	11.2
565	Ginsterweg	10.9	10.9
565	Hutäcker	9.6	9.6
565	Johanneszentrum	0.0	1.4
565	Karl-Speier-Str.	0.0	14.2
565	Kettelerstr.	22.4	22.4
565	Klostertor	0.0	5.0
565	Museum Lothar Fischer	0.0	18.4
565	Saarlandstr.	14.4	14.4
565	Schlossbad	0.0	15.8
565	Theo-Betz-Platz	0.0	62.0
565	Turnerheim	2.2	2.2
565	Volksfestplatz	0.0	15.2
565	Weißenfeldplatz	1.6	1.6
565	Wolfstein Hl. Kreuz	6.3	6.3
565	Wolfstein Siedlung	13.1	13.1
565	Zedernweg	9.4	9.4
566	Neumarkt Bahnhof	0.0	71.5
566	Badstr.	1.5	1.5
566	Gotenstr.	43.9	43.9
566	Höhenberg im Tal	14.5	14.5
566	Mariahilfstr.	32.8	32.8
566	St. Helena	2.9	2.9
566	Sturmwiese	4.4	4.4
566	Theo-Betz-Platz	0.0	57.4
566	Voggenthal Ort	2.1	2.1
566	Ziegelhüttenweg	5.4	5.4
567	Neumarkt Bahnhof	0.0	57.0
567	Ärztehaus	12.9	24.0
567	Dientzenhoferstr.	1.3	1.3
567	Fa. Klebl	5.5	5.5
567	Finanzamt	24.7	26.3
567	Friedhof	3.2	3.2
567	Kerschensteinerstr.	25.9	48.6
567	Lähr	11.0	11.0
567	Nobelstr.	4.9	4.9
567	Oberer Lährer Weg	1.5	1.5
567	Regensburger Str.	15.0	26.7
567	Schönwerthstr.	2.2	2.5
567	Schweningerstr.	3.9	3.9
567	Weinberger Str. / Schule	7.4	7.4
567	Wildbadstr.	6.3	6.3
568	Neumarkt Bahnhof	0.0	131.3
568	Ärztehaus	0.0	11.1
568	Berufsschulzentrum	56.8	56.8
568	Deininger Weg / Sportz.	3.6	3.6
568	Fa. Bionorica	4.6	4.6
568	Fa. Dehn	1.2	1.2
568	Fa. Pfleiderer	1.6	1.6
568	Finanzamt	0.0	1.6
568	Förstersteig	5.5	5.5
568	Hasenheide Kirche	8.3	8.3
568	Hasenheide Schule	31.6	31.6
568	Ingolstädter Str.	6.5	6.5
568	Kerschensteinerstr.	0.0	22.6
568	Ludwig-Wifling-Str.	7.5	7.5
568	Medererstr.	4.6	4.6
568	Regensburger Str.	0.0	11.7
568	Schönwerthstr.	0.0	0.3
568	Stadtwerke	36.8	36.8
569	Neumarkt Bahnhof	0.0	29.0
569	Oberer Markt	0.0	1.2
569	Rathaus	0.0	9.7
569	Ramoldplatz (Berngau) nur bis 09/24	2.6	2.6
569	Reifenstein (Berngau) nur bis 09/24	1.7	1.7
569	Alois-Senefelder-Str.	0.0	0.0
569	Fa. Aptiv	0.1	0.1
569	Freystädter Str.	0.8	0.8
569	Gansbrauerei	16.4	16.4
569	Johanneszentrum	0.0	3.3
569	Klebl Bauzentrum	5.1	5.1
569	Max-Künzel-Str.	4.8	4.8
569	Moosweiherstr.	11.4	11.4
569	Rebhuhnstr.	1.6	1.6
569	Renauweg (Stauf)	4.4	4.4
569	Schlossstr.	3.7	3.7
569	Stauf Kirche	7.3	7.3
569	Wallensteinstr.	2.1	2.1
569	Woffenbach Schule	5.9	5.9
569	Woffenbach Zentrum	8.4	8.4
570	Neumarkt Bahnhof	0.0	53.4
570	Oberer Markt	0.0	22.9
570	Rathaus	0.0	26.0
570	Am Letten	1.9	1.9
570	BRK-Altenheim	4.0	4.0
570	Johanneszentrum	0.0	9.9
570	Kreuzstr.	0.0	10.9
570	Meuselstr.	0.0	8.1
570	Tyrolsberger Str.	6.8	6.8
570	Volksfestplatz	0.0	10.7
570	Woffenbacher Str.	0.0	5.5
570	Woffenbach Kirche	9.9	9.9"""
        
        stop_dict = {}
        for line in raw_data.strip().split('\n'):
            parts = line.split('\t')
            if len(parts) >= 4:
                route_num, stop_name, weekday_str, total_str = parts[0], parts[1], parts[2], parts[3]
                
                # Handle empty weekday values
                weekday = float(weekday_str) if weekday_str else 0.0
                total = float(total_str) if total_str else 0.0
                
                if stop_name not in stop_dict:
                    stop = BusStop(stop_name, weekday, total, [route_num])
                    stop_dict[stop_name] = stop
                    self.stops.append(stop)
                else:
                    # Accumulate passengers for stops served by multiple routes
                    stop_dict[stop_name].passengers_weekday += weekday
                    stop_dict[stop_name].passengers_total += total
                    if route_num not in stop_dict[stop_name].route_numbers:
                        stop_dict[stop_name].route_numbers.append(route_num)
                
                self.routes[route_num].append(stop_dict[stop_name])
    
    def _initialize_current_schedules(self):
        """Initialize current schedules based on typical German bus operations"""
        for route_num, stops in self.routes.items():
            total_passengers = sum(stop.passengers_total for stop in stops)
            
            # Current typical frequencies (before optimization)
            if route_num in ['561', '562', '563']:  # Main routes
                current_peak_freq, current_offpeak_freq = 15, 30
            elif route_num in ['564', '565', '566']:  # Secondary routes
                current_peak_freq, current_offpeak_freq = 20, 40
            else:  # Peripheral routes
                current_peak_freq, current_offpeak_freq = 30, 60
            
            self.current_schedules[route_num] = {
                'frequency_peak': current_peak_freq,
                'frequency_offpeak': current_offpeak_freq,
                'service_hours': (6, 22),
                'daily_trips': self._calculate_trips(current_peak_freq, current_offpeak_freq, (6, 22)),
                'total_passengers': total_passengers
            }
    
    def _calculate_trips(self, peak_freq, offpeak_freq, service_hours):
        """Calculate total daily trips based on frequency and hours"""
        start_hour, end_hour = service_hours
        peak_hours = 4  # 2 hours morning + 2 hours evening peak
        offpeak_hours = (end_hour - start_hour) - peak_hours
        
        peak_trips = (peak_hours * 60) // peak_freq
        offpeak_trips = (offpeak_hours * 60) // offpeak_freq
        
        return peak_trips + offpeak_trips
    
    def calculate_route_metrics(self, route_num):
        """Calculate comprehensive metrics for a route"""
        stops = self.routes[route_num]
        current_schedule = self.current_schedules[route_num]
        
        total_passengers = sum(stop.passengers_total for stop in stops)
        daily_trips = current_schedule['daily_trips']
        
        # Assume bus capacity of 80 passengers and operating cost of €2 per km
        bus_capacity = 80
        cost_per_trip = 25  # Average cost per trip in euros
        
        occupancy_rate = (total_passengers / daily_trips) / bus_capacity if daily_trips > 0 else 0
        cost_per_passenger = (daily_trips * cost_per_trip) / total_passengers if total_passengers > 0 else float('inf')
        efficiency_score = total_passengers / len(stops) if stops else 0
        revenue_potential = total_passengers * 2.5  # Average fare €2.50
        
        return RouteMetrics(
            passengers_per_day=total_passengers,
            efficiency_score=efficiency_score,
            cost_per_passenger=cost_per_passenger,
            occupancy_rate=min(occupancy_rate, 1.0),
            revenue_potential=revenue_potential
        )
    
    def optimize_route_frequency(self, route_num):
        """Determine optimal frequency based on multiple factors"""
        metrics = self.calculate_route_metrics(route_num)
        stops = self.routes[route_num]
        
        # Factor 1: Passenger demand
        demand_score = min(metrics.passengers_per_day / 100, 3.0)  # Cap at 3x
        
        # Factor 2: Zone importance (core areas need better service)
        core_stops = len([s for s in stops if s.zone == "core"])
        zone_score = 1.0 + (core_stops / len(stops)) * 0.5 if stops else 1.0
        
        # Factor 3: Current occupancy (if too high, increase frequency)
        occupancy_score = 1.0 + max(0, metrics.occupancy_rate - 0.7) * 2
        
        # Factor 4: Network connectivity
        connectivity_score = 1.0 + (len(stops) / 20) * 0.3  # More stops = higher connectivity
        
        # Factor 5: Cost efficiency
        cost_score = max(0.5, 2.0 - (metrics.cost_per_passenger / 5))  # Lower cost = higher score
        
        # Combined optimization score
        optimization_multiplier = (demand_score * zone_score * occupancy_score * connectivity_score * cost_score) / 5
        
        # Base frequencies
        base_peak, base_offpeak = 20, 40
        
        # Apply optimization
        optimal_peak = max(5, int(base_peak / optimization_multiplier))
        optimal_offpeak = max(10, int(base_offpeak / optimization_multiplier))
        
        # Determine service hours based on demand
        if metrics.passengers_per_day > 200:
            service_hours = (5, 23)
        elif metrics.passengers_per_day > 50:
            service_hours = (6, 22)
        else:
            service_hours = (7, 21)
        
        return {
            'frequency_peak': optimal_peak,
            'frequency_offpeak': optimal_offpeak,
            'service_hours': service_hours,
            'daily_trips': self._calculate_trips(optimal_peak, optimal_offpeak, service_hours),
            'optimization_factors': {
                'demand_score': demand_score,
                'zone_score': zone_score,
                'occupancy_score': occupancy_score,
                'connectivity_score': connectivity_score,
                'cost_score': cost_score,
                'final_multiplier': optimization_multiplier
            }
        }
    
    def generate_recommendations(self):
        """Generate specific recommendations for each route"""
        self.recommendations = []
        
        for route_num in self.routes.keys():
            current = self.current_schedules[route_num]
            metrics = self.calculate_route_metrics(route_num)
            optimized = self.optimize_route_frequency(route_num)
            
            # Store optimized schedule
            self.optimized_schedules[route_num] = optimized
            
            # Calculate changes
            freq_change_peak = ((optimized['frequency_peak'] - current['frequency_peak']) / current['frequency_peak']) * 100
            freq_change_offpeak = ((optimized['frequency_offpeak'] - current['frequency_offpeak']) / current['frequency_offpeak']) * 100
            trips_change = optimized['daily_trips'] - current['daily_trips']
            
            # Determine recommendation type
            if abs(freq_change_peak) < 5 and abs(freq_change_offpeak) < 5:
                recommendation_type = "maintain_current"
                action = "Keep Current Schedule"
                reason = "Current frequency is optimal"
            elif freq_change_peak < -15 or freq_change_offpeak < -15:
                recommendation_type = "increase_frequency"
                action = "Increase Frequency"
                reason = f"High demand ({metrics.passengers_per_day:.0f} passengers/day) and occupancy ({metrics.occupancy_rate:.1%})"
            elif freq_change_peak > 25 or freq_change_offpeak > 25:
                recommendation_type = "decrease_frequency"
                action = "Reduce Frequency"
                reason = f"Low utilization ({metrics.passengers_per_day:.0f} passengers/day, cost €{metrics.cost_per_passenger:.2f}/passenger)"
            else:
                recommendation_type = "adjust_frequency"
                action = "Fine-tune Frequency"
                reason = "Optimize for better efficiency"
            
            # Special cases
            if metrics.passengers_per_day < 20:
                recommendation_type = "consider_cancellation"
                action = "Consider Route Cancellation"
                reason = f"Very low ridership ({metrics.passengers_per_day:.0f} passengers/day)"
            elif len(self.routes[route_num]) < 5 and metrics.passengers_per_day < 50:
                recommendation_type = "merge_with_other"
                action = "Consider Merging with Adjacent Route"
                reason = "Short route with low demand could be combined"
            
            self.recommendations.append({
                'route': route_num,
                'type': recommendation_type,
                'action': action,
                'reason': reason,
                'current_metrics': metrics,
                'frequency_changes': {
                    'peak_change_percent': freq_change_peak,
                    'offpeak_change_percent': freq_change_offpeak,
                    'trips_change': trips_change
                },
                'cost_impact': trips_change * 25,  # €25 per trip
                'passenger_impact': metrics.passengers_per_day * (1 + (trips_change / current['daily_trips']) * 0.3) if current['daily_trips'] > 0 else 0
            })
    
    def print_before_after_analysis(self):
        """Print comprehensive before/after comparison"""
        print("🚌" * 30)
        print("        NEUMARKT BUS NETWORK: BEFORE vs AFTER OPTIMIZATION")
        print("🚌" * 30)
        
        # Network summary
        total_current_trips = sum(schedule['daily_trips'] for schedule in self.current_schedules.values())
        total_optimized_trips = sum(schedule['daily_trips'] for schedule in self.optimized_schedules.values())
        total_passengers = sum(stop.passengers_total for stop in self.stops)
        
        print(f"\n📊 NETWORK OVERVIEW:")
        print(f"   • Total Routes Analyzed: {len(self.routes)}")
        print(f"   • Total Bus Stops: {len(self.stops)}")
        print(f"   • Total Daily Passengers: {total_passengers:.0f}")
        print(f"   • Current Daily Trips: {total_current_trips}")
        print(f"   • Optimized Daily Trips: {total_optimized_trips}")
        print(f"   • Net Trip Change: {total_optimized_trips - total_current_trips:+d} ({((total_optimized_trips - total_current_trips) / total_current_trips * 100):+.1f}%)")
        print(f"   • Estimated Cost Impact: €{(total_optimized_trips - total_current_trips) * 25:+,.0f} per day")
        
        # Recommendations summary
        print(f"\n🎯 RECOMMENDATION SUMMARY:")
        rec_counts = defaultdict(int)
        for rec in self.recommendations:
            rec_counts[rec['type']] += 1
        
        action_icons = {
            "increase_frequency": "⬆️ INCREASE",
            "decrease_frequency": "⬇️ DECREASE", 
            "maintain_current": "✅ MAINTAIN",
            "adjust_frequency": "🔧 ADJUST",
            "consider_cancellation": "❌ CANCEL",
            "merge_with_other": "🔄 MERGE"
        }
        
        for rec_type, count in rec_counts.items():
            icon = action_icons.get(rec_type, "📝")
            print(f"   {icon}: {count} route(s)")
        
        # Detailed route analysis
        print(f"\n📈 DETAILED ROUTE ANALYSIS:")
        print("=" * 100)
        
        for rec in sorted(self.recommendations, key=lambda x: x['current_metrics'].passengers_per_day, reverse=True):
            route_num = rec['route']
            current = self.current_schedules[route_num]
            optimized = self.optimized_schedules[route_num]
            metrics = rec['current_metrics']
            
            print(f"\n🚌 ROUTE {route_num}:")
            print(f"   📊 Current Performance:")
            print(f"      • Daily Passengers: {metrics.passengers_per_day:.0f}")
            print(f"      • Occupancy Rate: {metrics.occupancy_rate:.1%}")
            print(f"      • Cost per Passenger: €{metrics.cost_per_passenger:.2f}")
            print(f"      • Efficiency Score: {metrics.efficiency_score:.1f} passengers/stop")
            
            print(f"   ⏰ Schedule Comparison:")
            print(f"      • Peak Frequency:    {current['frequency_peak']:2d} min → {optimized['frequency_peak']:2d} min ({rec['frequency_changes']['peak_change_percent']:+.0f}%)")
            print(f"      • Off-Peak Frequency: {current['frequency_offpeak']:2d} min → {optimized['frequency_offpeak']:2d} min ({rec['frequency_changes']['offpeak_change_percent']:+.0f}%)")
            print(f"      • Service Hours:     {current['service_hours'][0]:02d}:00-{current['service_hours'][1]:02d}:00 → {optimized['service_hours'][0]:02d}:00-{optimized['service_hours'][1]:02d}:00")
            print(f"      • Daily Trips:       {current['daily_trips']:2d} → {optimized['daily_trips']:2d} ({rec['frequency_changes']['trips_change']:+d})")
            
            print(f"   🎯 Recommendation: {rec['action']}")
            print(f"      • Reasoning: {rec['reason']}")
            print(f"      • Cost Impact: €{rec['cost_impact']:+,.0f} per day")
            print(f"      • Expected Ridership: {rec['passenger_impact']:.0f} passengers/day ({(rec['passenger_impact'] - metrics.passengers_per_day):+.0f})")
            
            # Show optimization factors
            factors = optimized['optimization_factors']
            print(f"   🔍 Optimization Factors:")
            print(f"      • Demand Score: {factors['demand_score']:.2f} | Zone Score: {factors['zone_score']:.2f} | Occupancy Score: {factors['occupancy_score']:.2f}")
            print(f"      • Connectivity Score: {factors['connectivity_score']:.2f} | Cost Score: {factors['cost_score']:.2f}")
            print(f"      • Final Multiplier: {factors['final_multiplier']:.2f}")
            
            # Show key stops
            key_stops = sorted(self.routes[route_num], key=lambda x: x.passengers_total, reverse=True)[:3]
            if key_stops:
                stop_info = [f"{s.name} ({s.passengers_total:.0f})" for s in key_stops]
                print(f"   🚏 Key Stops: {' • '.join(stop_info)}")
        
        # New route suggestions
        print(f"\n💡 NEW ROUTE SUGGESTIONS:")
        new_route_suggestions = self._suggest_new_routes()
        if new_route_suggestions:
            for i, suggestion in enumerate(new_route_suggestions, 1):
                print(f"   {i}. {suggestion['type']}: {suggestion['description']}")
                print(f"      • Estimated Ridership: {suggestion['potential_passengers']:.0f} passengers/day")
                print(f"      • Key Connections: {', '.join(suggestion['key_stops'][:3])}")
        else:
            print("   No new routes recommended based on current network coverage.")
        
        return self.recommendations
    
    def _suggest_new_routes(self):
        """Suggest new routes based on gaps in the network"""
        suggestions = []
        
        # Find high-demand stops with limited route options
        underserved_stops = [stop for stop in self.stops 
                           if len(stop.route_numbers) == 1 and stop.passengers_total > 30]
        
        if len(underserved_stops) >= 3:
            suggestions.append({
                'type': 'New Connector Route',
                'description': f'Connect {len(underserved_stops)} underserved high-demand stops',
                'potential_passengers': sum(s.passengers_total for s in underserved_stops) * 0.6,
                'key_stops': [s.name for s in underserved_stops[:5]]
            })
        
        # Express route for major hubs
        major_hubs = [stop for stop in self.stops 
                     if stop.zone == "core" and stop.passengers_total > 100]
        
        if len(major_hubs) >= 3:
            suggestions.append({
                'type': 'Express Hub Route',
                'description': f'Express service connecting {len(major_hubs)} major hubs',
                'potential_passengers': sum(s.passengers_total for s in major_hubs) * 0.25,
                'key_stops': [s.name for s in major_hubs]
            })
        
        # Night service for high-demand routes
        high_demand_routes = [route for route, stops in self.routes.items() 
                             if sum(s.passengers_total for s in stops) > 300]
        
        if high_demand_routes:
            suggestions.append({
                'type': 'Night Service Extension',
                'description': f'Extend service hours for routes {", ".join(high_demand_routes[:3])}',
                'potential_passengers': sum(sum(s.passengers_total for s in self.routes[r]) 
                                          for r in high_demand_routes[:3]) * 0.15,
                'key_stops': ['Late evening service', 'Extended weekend hours']
            })
        
        return suggestions
    
    def export_comprehensive_comparison(self, filename_base="neumarkt_optimization"):
        """Export detailed before/after comparison to CSV files"""
        
        # 1. Route comparison summary
        with open(f"{filename_base}_route_comparison.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'route', 'recommendation', 'current_passengers', 'current_peak_freq', 'current_offpeak_freq', 
                'current_daily_trips', 'optimized_peak_freq', 'optimized_offpeak_freq', 'optimized_daily_trips',
                'frequency_change_peak_pct', 'frequency_change_offpeak_pct', 'trips_change', 
                'cost_impact_eur', 'occupancy_rate', 'cost_per_passenger', 'efficiency_score'
            ])
            
            for rec in self.recommendations:
                route_num = rec['route']
                current = self.current_schedules[route_num]
                optimized = self.optimized_schedules[route_num]
                metrics = rec['current_metrics']
                
                writer.writerow([
                    route_num, rec['action'], metrics.passengers_per_day,
                    current['frequency_peak'], current['frequency_offpeak'], current['daily_trips'],
                    optimized['frequency_peak'], optimized['frequency_offpeak'], optimized['daily_trips'],
                    rec['frequency_changes']['peak_change_percent'],
                    rec['frequency_changes']['offpeak_change_percent'],
                    rec['frequency_changes']['trips_change'],
                    rec['cost_impact'], metrics.occupancy_rate, metrics.cost_per_passenger,
                    metrics.efficiency_score
                ])
        
        # 2. Detailed recommendations
        with open(f"{filename_base}_recommendations.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'route', 'recommendation_type', 'action', 'reasoning', 'priority',
                'implementation_cost', 'expected_ridership_change', 'payback_period_days'
            ])
            
            for rec in self.recommendations:
                # Calculate priority based on passenger impact and cost
                if rec['current_metrics'].passengers_per_day > 200:
                    priority = "High"
                elif rec['current_metrics'].passengers_per_day > 50:
                    priority = "Medium"
                else:
                    priority = "Low"
                
                # Estimate payback period
                daily_revenue_change = (rec['passenger_impact'] - rec['current_metrics'].passengers_per_day) * 2.5
                payback_days = abs(rec['cost_impact'] / daily_revenue_change) if daily_revenue_change != 0 else float('inf')
                
                writer.writerow([
                    rec['route'], rec['type'], rec['action'], rec['reason'], priority,
                    abs(rec['cost_impact']), 
                    rec['passenger_impact'] - rec['current_metrics'].passengers_per_day,
                    payback_days if payback_days != float('inf') else 'N/A'
                ])
        
        # 3. Stop analysis with route recommendations
        with open(f"{filename_base}_stop_analysis.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'stop_name', 'total_passengers', 'weekday_passengers', 'zone', 'priority',
                'current_routes', 'route_count', 'demand_pattern', 'service_recommendation'
            ])
            
            for stop in sorted(self.stops, key=lambda x: x.passengers_total, reverse=True):
                # Generate service recommendation for stop
                if len(stop.route_numbers) == 1 and stop.passengers_total > 50:
                    service_rec = "Add alternative route"
                elif stop.passengers_total > 100 and stop.zone == "core":
                    service_rec = "Increase frequency on all routes"
                elif stop.passengers_total < 5:
                    service_rec = "Consider stop consolidation"
                else:
                    service_rec = "Maintain current service"
                
                writer.writerow([
                    stop.name, stop.passengers_total, stop.passengers_weekday,
                    stop.zone, stop.priority, '|'.join(stop.route_numbers),
                    len(stop.route_numbers), stop.demand_pattern, service_rec
                ])
        
        # 4. Financial impact summary
        with open(f"{filename_base}_financial_impact.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'category', 'current_daily_cost', 'optimized_daily_cost', 'daily_change',
                'annual_change', 'current_revenue_potential', 'optimized_revenue_potential',
                'net_annual_impact'
            ])
            
            current_cost = sum(s['daily_trips'] for s in self.current_schedules.values()) * 25
            optimized_cost = sum(s['daily_trips'] for s in self.optimized_schedules.values()) * 25
            daily_cost_change = optimized_cost - current_cost
            annual_cost_change = daily_cost_change * 365
            
            current_revenue = sum(stop.passengers_total for stop in self.stops) * 2.5
            optimized_revenue = sum(rec['passenger_impact'] for rec in self.recommendations) * 2.5
            revenue_change = optimized_revenue - current_revenue
            annual_revenue_change = revenue_change * 365
            
            net_annual_impact = annual_revenue_change - annual_cost_change
            
            writer.writerow([
                'Total Network', current_cost, optimized_cost, daily_cost_change,
                annual_cost_change, current_revenue, optimized_revenue, net_annual_impact
            ])
        
        print(f"\n📁 COMPREHENSIVE ANALYSIS EXPORTED:")
        print(f"   • {filename_base}_route_comparison.csv - Before/after route comparison")
        print(f"   • {filename_base}_recommendations.csv - Detailed recommendations with priorities")
        print(f"   • {filename_base}_stop_analysis.csv - Individual stop analysis")
        print(f"   • {filename_base}_financial_impact.csv - Cost-benefit analysis")
    
    def generate_implementation_plan(self):
        """Generate a phased implementation plan"""
        print(f"\n📋 IMPLEMENTATION PLAN:")
        print("=" * 60)
        
        # Phase 1: Quick wins (low cost, high impact)
        phase1 = [rec for rec in self.recommendations 
                 if abs(rec['cost_impact']) < 500 and rec['passenger_impact'] > rec['current_metrics'].passengers_per_day * 1.1]
        
        # Phase 2: Major improvements (high cost, high impact)
        phase2 = [rec for rec in self.recommendations 
                 if abs(rec['cost_impact']) >= 500 and rec['passenger_impact'] > rec['current_metrics'].passengers_per_day * 1.05]
        
        # Phase 3: Optimization and cuts (cost reduction focus)
        phase3 = [rec for rec in self.recommendations 
                 if rec['cost_impact'] < 0 or rec['type'] in ['consider_cancellation', 'merge_with_other']]
        
        phases = [
            ("PHASE 1: Quick Wins (Month 1-2)", phase1),
            ("PHASE 2: Major Improvements (Month 3-6)", phase2), 
            ("PHASE 3: Cost Optimization (Month 6-12)", phase3)
        ]
        
        for phase_name, recommendations in phases:
            if recommendations:
                print(f"\n🚀 {phase_name}:")
                total_cost = sum(abs(rec['cost_impact']) for rec in recommendations)
                total_passenger_impact = sum(rec['passenger_impact'] - rec['current_metrics'].passengers_per_day for rec in recommendations)
                
                print(f"   Total Implementation Cost: €{total_cost:,.0f}")
                print(f"   Expected Ridership Change: {total_passenger_impact:+.0f} passengers/day")
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. Route {rec['route']}: {rec['action']}")
                    print(f"      Cost: €{abs(rec['cost_impact']):,.0f} | Passenger Change: {rec['passenger_impact'] - rec['current_metrics'].passengers_per_day:+.0f}")

def main():
    print("🚀 Starting Advanced Neumarkt Bus Network Optimization...")
    print("   Analyzing current vs. optimized schedules with detailed recommendations")
    
    optimizer = SmartBusOptimizer()
    optimizer.generate_recommendations()
    recommendations = optimizer.print_before_after_analysis()
    optimizer.export_comprehensive_comparison()
    optimizer.generate_implementation_plan()
    
    print(f"\n✅ OPTIMIZATION ANALYSIS COMPLETE!")
    print(f"📊 Analyzed {len(optimizer.routes)} routes with {len(optimizer.stops)} stops")
    print(f"🎯 Generated {len(recommendations)} specific recommendations")
    print(f"💰 Total network optimization potential identified")
    print(f"📂 Detailed reports exported to CSV files")
    
    return optimizer

if __name__ == "__main__":
    main()