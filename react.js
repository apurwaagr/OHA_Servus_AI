import React, { useState, useEffect, useCallback } from 'react';
import { MapPin, Navigation, Clock, Calendar, Settings, Search, Heart, ChevronRight, Bus, Train, Walk, Bike, Zap, Droplets, Home, Car, Info, Menu, X } from 'lucide-react';

const GTFSOTPApp = () => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureTime, setDepartureTime] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [mode, setMode] = useState('TRANSIT,WALK');
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('planner');
  const [recentSearches, setRecentSearches] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Initialize with current date/time
  useEffect(() => {
    const now = new Date();
    setDepartureDate(now.toISOString().split('T')[0]);
    setDepartureTime(now.toTimeString().slice(0, 5));
  }, []);

  // Load saved data
  useEffect(() => {
    const saved = {
      recent: JSON.parse(localStorage.getItem('recentSearches') || '[]'),
      favs: JSON.parse(localStorage.getItem('favorites') || '[]')
    };
    setRecentSearches(saved.recent);
    setFavorites(saved.favs);
  }, []);

  const getModeIcon = (mode) => {
    const icons = {
      'BUS': <Bus className="w-4 h-4" />,
      'RAIL': <Train className="w-4 h-4" />,
      'WALK': <Walk className="w-4 h-4" />,
      'BICYCLE': <Bike className="w-4 h-4" />,
      'CAR': <Car className="w-4 h-4" />,
      'TRANSIT': <Bus className="w-4 h-4" />
    };
    return icons[mode] || <Navigation className="w-4 h-4" />;
  };

  const getModeColor = (mode) => {
    const colors = {
      'BUS': 'bg-blue-500',
      'RAIL': 'bg-red-500',
      'WALK': 'bg-green-500',
      'BICYCLE': 'bg-yellow-500',
      'CAR': 'bg-gray-500'
    };
    return colors[mode] || 'bg-blue-500';
  };

  const planTrip = async () => {
    if (!origin || !destination) {
      alert('Bitte geben Sie Start und Ziel ein');
      return;
    }

    setLoading(true);

    // Save to recent searches
    const search = { origin, destination, timestamp: Date.now() };
    const updated = [search, ...recentSearches.filter(s =>
      s.origin !== origin || s.destination !== destination
    )].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));

    // Real API call to OTP backend
    try {
      // OTP expects lat/lon or place names. Here we use the text input directly as 'fromPlace' and 'toPlace'.
      const params = new URLSearchParams({
        fromPlace: origin,
        toPlace: destination,
        date: departureDate,
        time: departureTime,
        mode: mode,
        locale: 'de',
        numItineraries: 3
      });
      const response = await fetch('http://localhost:8080/otp/routers/default/plan?' + params.toString());
      if (!response.ok) throw new Error('Fehler bei der Verbindung zum Routenplaner');
      const data = await response.json();
      // Map OTP response to UI format
      const newRoutes = (data.plan?.itineraries || []).map((it, idx) => ({
        id: idx + 1,
        duration: Math.round(it.duration / 60),
        transfers: it.transfers,
        departureTime: new Date(it.startTime).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
        arrivalTime: new Date(it.endTime).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
        fare: data.fare ? `${(data.fare?.fare?.regular?.cents / 100).toFixed(2)} €` : '',
        legs: it.legs.map(leg => ({
          mode: leg.mode,
          from: leg.from.name,
          to: leg.to.name,
          duration: Math.round(leg.duration / 60),
          distance: leg.distance ? `${Math.round(leg.distance)} m` : undefined,
          routeNumber: leg.route?.shortName,
          operator: leg.agency?.name
        }))
      }));
      setRoutes(newRoutes);
    } catch (err) {
      alert(err.message || 'Unbekannter Fehler');
      setRoutes([]);
    } finally {
      setLoading(false);
    }
  };

  const addMinutes = (time, minutes) => {
    const [hours, mins] = time.split(':').map(Number);
    const totalMins = hours * 60 + mins + minutes;
    const newHours = Math.floor(totalMins / 60) % 24;
    const newMins = totalMins % 60;
    return `${String(newHours).padStart(2, '0')}:${String(newMins).padStart(2, '0')}`;
  };

  const swapLocations = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const saveFavorite = () => {
    if (!origin || !destination) return;
    const fav = { origin, destination, id: Date.now() };
    const updated = [...favorites, fav];
    setFavorites(updated);
    localStorage.setItem('favorites', JSON.stringify(updated));
    alert('Route wurde zu Favoriten hinzugefügt!');
  };

  const loadSearch = (search) => {
    setOrigin(search.origin);
    setDestination(search.destination);
    setActiveTab('planner');
  };

  const removeFavorite = (id) => {
    const updated = favorites.filter(f => f.id !== id);
    setFavorites(updated);
    localStorage.setItem('favorites', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with SWN Branding */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* SWN Logo Area */}
              <div className="flex items-center space-x-2">
                <div className="flex -space-x-2">
                  <Heart className="w-8 h-8 text-blue-600 fill-blue-600" />
                  <Heart className="w-8 h-8 text-green-500 fill-green-500" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">
                    SWN Mobilitätsplaner
                  </h1>
                  <p className="text-xs text-gray-600 font-medium">Wir. Können. Zukunft.</p>
                </div>
              </div>
            </div>

            {/* Desktop Menu */}
            <nav className="hidden md:flex items-center space-x-6">
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Zap className="w-5 h-5" />
                <span className="text-sm font-medium">Energie</span>
              </button>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Droplets className="w-5 h-5" />
                <span className="text-sm font-medium">Wasser</span>
              </button>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Bus className="w-5 h-5" />
                <span className="text-sm font-medium">Stadtbus</span>
              </button>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <Info className="w-5 h-5" />
                <span className="text-sm font-medium">Service</span>
              </button>
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b shadow-lg">
          <div className="px-4 py-2 space-y-2">
            {['Energie', 'Wasser', 'Stadtbus', 'Service'].map((item, index) => (
              <button key={index} className="w-full text-left py-2 px-3 hover:bg-gray-100 rounded-lg transition-colors">
                <span className="text-gray-700 font-medium">{item}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-white border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'planner', label: 'Reiseplaner', icon: <Navigation className="w-4 h-4" /> },
              { id: 'recent', label: 'Verlauf', icon: <Clock className="w-4 h-4" /> },
              { id: 'favorites', label: 'Favoriten', icon: <Heart className="w-4 h-4" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-3 px-1 border-b-3 font-medium text-sm transition-all whitespace-nowrap ${activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'planner' && (
          <div className="space-y-6">
            {/* Trip Planner Card */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="space-y-4">
                {/* Route Input */}
                <div className="relative">
                  <div className="space-y-3">
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3.5 w-5 h-5 text-green-600" />
                      <input
                        type="text"
                        placeholder="Von: Adresse oder Haltestelle eingeben..."
                        value={origin}
                        onChange={(e) => setOrigin(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                    </div>

                    <button
                      onClick={swapLocations}
                      className="absolute right-3 top-11 z-10 bg-white border-2 border-gray-200 rounded-full p-2 hover:bg-gray-50 transition-all shadow-md"
                      title="Tauschen"
                    >
                      <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                      </svg>
                    </button>

                    <div className="relative">
                      <MapPin className="absolute left-3 top-3.5 w-5 h-5 text-red-600" />
                      <input
                        type="text"
                        placeholder="Nach: Adresse oder Haltestelle eingeben..."
                        value={destination}
                        onChange={(e) => setDestination(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                    </div>
                  </div>
                </div>

                {/* Date, Time and Options */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="relative">
                    <Calendar className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                    <input
                      type="date"
                      value={departureDate}
                      onChange={(e) => setDepartureDate(e.target.value)}
                      className="w-full pl-11 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div className="relative">
                    <Clock className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                    <input
                      type="time"
                      value={departureTime}
                      onChange={(e) => setDepartureTime(e.target.value)}
                      className="w-full pl-11 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="TRANSIT,WALK">ÖPNV & Fußweg</option>
                    <option value="TRANSIT,BICYCLE">ÖPNV & Fahrrad</option>
                    <option value="TRANSIT,CAR">ÖPNV & Auto (P+R)</option>
                    <option value="BICYCLE">Nur Fahrrad</option>
                    <option value="WALK">Nur Fußweg</option>
                  </select>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={planTrip}
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Suche läuft...</span>
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5" />
                        <span>Verbindung suchen</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={saveFavorite}
                    className="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-all font-medium flex items-center justify-center space-x-2"
                  >
                    <Heart className="w-5 h-5" />
                    <span>Favorit</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Results */}
            {routes.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-bold text-gray-800">Verbindungen</h2>
                {routes.map((route) => (
                  <div key={route.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all cursor-pointer overflow-hidden">
                    <div className="p-4">
                      {/* Route Header */}
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center space-x-4">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-gray-800">{route.departureTime}</p>
                            <p className="text-xs text-gray-500">Abfahrt</p>
                          </div>
                          <div className="flex items-center space-x-2 text-gray-400">
                            <div className="w-16 h-0.5 bg-gray-300"></div>
                            <ChevronRight className="w-4 h-4" />
                            <div className="w-16 h-0.5 bg-gray-300"></div>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-gray-800">{route.arrivalTime}</p>
                            <p className="text-xs text-gray-500">Ankunft</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-green-600">{route.fare}</p>
                          <p className="text-sm text-gray-500">{route.duration} Min</p>
                          {route.transfers > 0 && (
                            <p className="text-xs text-gray-500">{route.transfers} Umstieg{route.transfers > 1 ? 'e' : ''}</p>
                          )}
                        </div>
                      </div>

                      {/* Route Legs */}
                      <div className="space-y-2 border-t pt-3">
                        {route.legs.map((leg, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${getModeColor(leg.mode)} text-white`}>
                              {getModeIcon(leg.mode)}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                {leg.routeNumber && (
                                  <span className="px-2 py-1 bg-gray-100 rounded text-xs font-bold text-gray-700">
                                    {leg.routeNumber}
                                  </span>
                                )}
                                <span className="text-sm text-gray-700">
                                  {leg.from} → {leg.to}
                                </span>
                              </div>
                              <div className="flex items-center space-x-3 mt-1">
                                <span className="text-xs text-gray-500">{leg.duration} Min</span>
                                {leg.distance && (
                                  <span className="text-xs text-gray-500">{leg.distance}</span>
                                )}
                                {leg.operator && (
                                  <span className="text-xs text-gray-500">{leg.operator}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'recent' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Letzte Suchen</h2>
            {recentSearches.length > 0 ? (
              <div className="space-y-3">
                {recentSearches.map((search, index) => (
                  <div
                    key={index}
                    onClick={() => loadSearch(search)}
                    className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Clock className="w-5 h-5 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-800">{search.origin} → {search.destination}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(search.timestamp).toLocaleString('de-DE')}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Noch keine Suchen vorhanden</p>
            )}
          </div>
        )}

        {activeTab === 'favorites' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Gespeicherte Routen</h2>
            {favorites.length > 0 ? (
              <div className="space-y-3">
                {favorites.map((fav) => (
                  <div
                    key={fav.id}
                    className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div
                        onClick={() => loadSearch(fav)}
                        className="flex items-center space-x-3 flex-1 cursor-pointer"
                      >
                        <Heart className="w-5 h-5 text-red-500 fill-red-500" />
                        <p className="font-medium text-gray-800">{fav.origin} → {fav.destination}</p>
                      </div>
                      <button
                        onClick={() => removeFavorite(fav.id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Noch keine Favoriten gespeichert</p>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 bg-gray-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="flex -space-x-1">
                  <Heart className="w-6 h-6 text-white fill-white" />
                  <Heart className="w-6 h-6 text-green-400 fill-green-400" />
                </div>
                <span className="font-bold">Stadtwerke Neumarkt</span>
              </div>
              <p className="text-sm text-gray-400">Wir. Können. Zukunft.</p>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Mobilität</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Stadtbus</a></li>
                <li><a href="#" className="hover:text-white transition-colors">E-Carsharing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Parkhäuser</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Services</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Schlossbad</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Energie</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Wasser</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Kontakt</h3>
              <p className="text-sm text-gray-400">
                Ingolstädter Str. 18<br />
                92318 Neumarkt i.d.OPf.<br />
                Tel: 09181 239-0
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-700 text-center text-sm text-gray-400">
            © 2025 Stadtwerke Neumarkt i.d.OPf. - GTFS OTP Tool
          </div>
        </div>
      </footer>
    </div>
  );
};

export default GTFSOTPApp;