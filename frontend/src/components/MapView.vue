<template>
  <div class="map-container">
    <!-- 로딩 중 표시 -->
    <div v-if="loading" class="loading">
      <p>지도를 로딩 중입니다...</p>
    </div>

    <!-- 에러 표시 -->
    <div v-if="error" class="error">
      <p>❌ {{ error }}</p>
    </div>

    <!-- 지도가 표시될 영역 -->
    <div ref="mapDiv" class="map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const mapDiv = ref(null);
const loading = ref(true);
const error = ref(null);
let map = null;

// ✅ Google Maps 스크립트를 최신 방식으로 로드
const loadGoogleMapsScript = () => {
  return new Promise((resolve, reject) => {
    // 이미 로드되어 있으면 바로 리턴
    if (window.google && window.google.maps) {
      resolve(window.google);
      return;
    }

    // script 태그 생성 - v=beta 추가 (최신 버전)
    const script = document.createElement('script');
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    
    // ✅ loading=async 추가하여 경고 제거
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,marker&loading=async&language=ko&v=beta`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      console.log('✅ 구글맵 스크립트 로드 완료');
      resolve(window.google);
    };

    script.onerror = () => {
      console.error('❌ 구글맵 스크립트 로드 실패');
      reject(new Error('구글맵 스크립트를 로드할 수 없습니다.'));
    };

    document.head.appendChild(script);
  });
};

// 지도 생성 함수
const createMap = async (google, location) => {
  // ✅ 최신 방식: google.maps.Map 생성
  const { Map } = await google.maps.importLibrary("maps");
  
  map = new Map(mapDiv.value, {
    center: location,
    zoom: 15,
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
    mapId: 'DEMO_MAP_ID' // AdvancedMarkerElement 사용을 위해 필요
  });

  console.log('✅ 지도 생성 완료');
  return map;
};

// ✅ 최신 방식으로 마커 생성
const createUserMarker = async (google, location) => {
  try {
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    
    // 사용자 위치 마커 (빨간색)
    const markerContent = document.createElement('div');
    markerContent.innerHTML = `
      <div style="
        width: 30px;
        height: 30px;
        background: #ef4444;
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      "></div>
    `;
    
    new AdvancedMarkerElement({
      map: map,
      position: location,
      content: markerContent,
      title: '현재 위치'
    });
  } catch (e) {
    console.error('마커 생성 실패:', e);
    // 폴백: 기본 마커 사용
    new google.maps.Marker({
      position: location,
      map: map,
      title: '현재 위치'
    });
  }
};

// 정확도 원 표시
const showAccuracyCircle = (google, location, accuracy) => {
  new google.maps.Circle({
    map: map,
    center: location,
    radius: accuracy,
    fillColor: '#4285F4',
    fillOpacity: 0.15,
    strokeColor: '#4285F4',
    strokeOpacity: 0.4,
    strokeWeight: 1,
  });
  
  console.log(`🎯 정확도 범위: 약 ${Math.round(accuracy)}m 이내`);
};

// ✅ 최신 Places API 사용
const searchNearbyPharmacies = async (google, location) => {
  try {
    // ✅ 새로운 방식: places library 사용
    const { Place } = await google.maps.importLibrary("places");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    
    // Nearby Search 요청
    const request = {
      textQuery: '약국',
      fields: ['displayName', 'location', 'formattedAddress', 'rating'],
      locationBias: {
        center: location,
        radius: 2000 // 2km
      },
      language: 'ko',
      maxResultCount: 20,
    };

    // ✅ 새로운 API: Place.searchNearby 대신 textSearch 사용
    const { places } = await Place.searchByText(request);

    if (places && places.length > 0) {
      console.log(`✅ 약국 ${places.length}개 발견`);

      places.forEach((place) => {
        // 마커 생성 (파란색)
        const markerContent = document.createElement('div');
        markerContent.innerHTML = `
          <div style="
            width: 24px;
            height: 24px;
            background: #3b82f6;
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          "></div>
        `;

        const marker = new AdvancedMarkerElement({
          map: map,
          position: place.location,
          content: markerContent,
          title: place.displayName
        });

        // 정보창
        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div style="padding: 12px; min-width: 200px;">
              <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700; color: #1e293b;">
                ${place.displayName || place.formattedAddress}
              </h3>
              ${place.formattedAddress ? 
                `<p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b; line-height: 1.5;">
                  📍 ${place.formattedAddress}
                </p>` : ''}
              ${place.rating ? 
                `<p style="margin: 0; font-size: 14px; color: #f59e0b; font-weight: 600;">
                  ⭐ ${place.rating} / 5
                </p>` : ''}
            </div>
          `
        });

        marker.addListener('click', () => {
          infoWindow.open(map, marker);
        });
      });

      loading.value = false;
    } else {
      console.log('주변 약국을 찾을 수 없습니다');
      loading.value = false;
    }
  } catch (e) {
    console.error('약국 검색 실패:', e);
    
    // ✅ 폴백: 기존 PlacesService 사용 (deprecated 경고 발생)
    searchNearbyPharmaciesFallback(google, location);
  }
};

// 폴백 함수 (구버전 API)
const searchNearbyPharmaciesFallback = (google, location) => {
  const service = new google.maps.places.PlacesService(map);

  const request = {
    location: location,
    radius: 2000,
    type: 'pharmacy',
    keyword: '약국'
  };

  service.nearbySearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results) {
      console.log(`✅ 약국 ${results.length}개 발견 (구버전 API)`);

      results.forEach((place) => {
        const marker = new google.maps.Marker({
          position: place.geometry.location,
          map: map,
          title: place.name
        });

        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div style="padding: 12px; min-width: 200px;">
              <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700; color: #1e293b;">${place.name}</h3>
              <p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b; line-height: 1.5;">📍 ${place.vicinity}</p>
              ${place.rating ? `<p style="margin: 0; font-size: 14px; color: #f59e0b; font-weight: 600;">⭐ ${place.rating} / 5</p>` : ''}
            </div>
          `
        });

        marker.addListener('click', () => {
          infoWindow.open(map, marker);
        });
      });

      loading.value = false;
    } else {
      console.warn('약국 검색 실패:', status);
      loading.value = false;
    }
  });
};

onMounted(async () => {
  try {
    console.log('구글맵 로딩 시작...');
    const google = await loadGoogleMapsScript();

    if (navigator.geolocation) {
      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      };
      
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          
          console.log('📍 현재 위치:', userLocation);
          console.log('📏 정확도:', position.coords.accuracy, '미터');

          await createMap(google, userLocation);
          await createUserMarker(google, userLocation);
          showAccuracyCircle(google, userLocation, position.coords.accuracy);
          await searchNearbyPharmacies(google, userLocation);
        },
        async (err) => {
          console.warn('위치 권한 거부 또는 실패:', err);
          const defaultLocation = { lat: 37.5665, lng: 126.9780 };
          
          await createMap(google, defaultLocation);
          await createUserMarker(google, defaultLocation);
          await searchNearbyPharmacies(google, defaultLocation);
          
          let errorMsg = '위치를 가져올 수 없습니다.';
          switch(err.code) {
            case err.PERMISSION_DENIED:
              errorMsg = '위치 권한이 거부되었습니다. 기본 위치(서울)로 표시합니다.';
              break;
            case err.POSITION_UNAVAILABLE:
              errorMsg = '위치 정보를 사용할 수 없습니다. 기본 위치(서울)로 표시합니다.';
              break;
            case err.TIMEOUT:
              errorMsg = '위치 요청 시간이 초과되었습니다. 기본 위치(서울)로 표시합니다.';
              break;
          }
          alert(errorMsg);
          loading.value = false;
        },
        options
      );
    } else {
      const defaultLocation = { lat: 37.5665, lng: 126.9780 };
      await createMap(google, defaultLocation);
      await createUserMarker(google, defaultLocation);
      await searchNearbyPharmacies(google, defaultLocation);
      loading.value = false;
    }

  } catch (err) {
    console.error('❌ 지도 로드 실패:', err);
    error.value = '지도를 로드할 수 없습니다: ' + err.message;
    loading.value = false;
  }
});
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.map {
  width: 100%;
  height: 100%;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.error {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #fee;
  color: #c00;
  padding: 10px 20px;
  border-radius: 4px;
  z-index: 10;
  max-width: 90%;
}
</style>