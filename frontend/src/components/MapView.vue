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

// Google Maps 스크립트를 동적으로 로드하는 함수
const loadGoogleMapsScript = () => {
  return new Promise((resolve, reject) => {
    // 이미 로드되어 있으면 바로 리턴
    if (window.google && window.google.maps) {
      resolve(window.google);
      return;
    }

    // script 태그 생성
    const script = document.createElement('script');
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&language=ko`;
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
const createMap = (google, location) => {
  map = new google.maps.Map(mapDiv.value, {
    center: location,
    zoom: 15,
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
  });

  // 현재 위치에 빨간 마커
  new google.maps.Marker({
    position: location,
    map: map,
    title: '현재 위치',
    icon: {
      url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    }
  });

  console.log('✅ 지도 생성 완료');
  return map;
};

// 주변 약국 검색 함수
const searchNearbyPharmacies = (google, location) => {
  const service = new google.maps.places.PlacesService(map);

  const request = {
    location: location,
    radius: 2000, // 2km
    type: 'pharmacy',
    keyword: '약국'
  };

  service.nearbySearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results) {
      console.log(`✅ 약국 ${results.length}개 발견`);

      results.forEach((place) => {
        const marker = new google.maps.Marker({
          position: place.geometry.location,
          map: map,
          title: place.name,
          icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
          }
        });

        // 정보창
        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div style="padding: 10px; min-width: 200px;">
              <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">${place.name}</h3>
              <p style="margin: 0; font-size: 14px; color: #666; line-height: 1.4;">${place.vicinity}</p>
              ${place.rating ? `<p style="margin: 8px 0 0 0; font-size: 14px;">⭐ ${place.rating} / 5</p>` : ''}
              ${place.opening_hours ? 
                `<p style="margin: 4px 0 0 0; font-size: 13px; color: ${place.opening_hours.open_now ? '#0a0' : '#a00'};">
                  ${place.opening_hours.open_now ? '✅ 영업 중' : '❌ 영업 종료'}
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
      console.warn('약국 검색 실패:', status);
      loading.value = false;
    }
  });
};

onMounted(async () => {
  try {
    // 1. Google Maps 스크립트 로드
    console.log('구글맵 로딩 시작...');
    const google = await loadGoogleMapsScript();

    // 2. 현재 위치 가져오기
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        // 성공
        (position) => {
          const userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          console.log('📍 현재 위치:', userLocation);

          createMap(google, userLocation);
          searchNearbyPharmacies(google, userLocation);
        },
        // 실패
        (err) => {
          console.warn('위치 권한 거부:', err);
          const defaultLocation = { lat: 37.5665, lng: 126.9780 }; // 서울 시청
          createMap(google, defaultLocation);
          searchNearbyPharmacies(google, defaultLocation);
          alert('위치 권한이 거부되었습니다. 기본 위치(서울)로 표시합니다.');
          loading.value = false;
        }
      );
    } else {
      // 브라우저가 위치 정보 미지원
      const defaultLocation = { lat: 37.5665, lng: 126.9780 };
      createMap(google, defaultLocation);
      searchNearbyPharmacies(google, defaultLocation);
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