//Funções de gerenciamento de parametros de bairros

import { cacheManager } from '../utils/cacheManager'
import { safeFetch } from '../utils/clientApi'

let polygonsCleaner: Map<string, google.maps.Polygon> = new Map()

export interface NeighborhoodInfo {
  id: number
  name: string
  type: string
}

export const clearAllPolygons = () => {
  polygonsCleaner.forEach((p) => {
    if (p) p.setMap(null)
  })
  polygonsCleaner.clear()
}

export const fetchAllNeighborhoods = async (cityName: string): Promise<NeighborhoodInfo[]> => {
  if (!cityName) return []

  const cacheNeighborhoods = `${cityName}-neighborhoods`

  try {
    const cached = cacheManager.get<NeighborhoodInfo[]>(cacheNeighborhoods)
    if (cached) return cached
  } catch (e) {
    console.warn('Erro ao ler cache da lista de bairros.')
  }

  const query = `
    [out:json];
    area["name"="${cityName}"]["admin_level"="8"]->.searchArea;
    (
      relation["admin_level"="10"](area.searchArea);
      way["admin_level"="10"](area.searchArea);
    );
    out tags;
  `

  const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`

  //OBS: Overpass é uma api muito instavel, porem é a unica opção para dar get em uma lista de bairros
  //Nominatim apenas retorna a latitude e longitude, porem não seus nomes.

  try {
    const response = await safeFetch(url)
    const data = await response.json()

    if (!data.elements) return []

    console.log(data.elements)

    const neighborhoodPackage = data.elements
      .map((el: any) => ({
        id: el.id,
        name: el.tags.name,
        type: el.type === 'relation' ? 'R' : 'W',
      }))
      .filter((n: NeighborhoodInfo) => n.name && n.name !== '')

    const sendNeighborhoods = [
      ...new Map<string, NeighborhoodInfo>(
        neighborhoodPackage.map((n: NeighborhoodInfo) => [n.name, n]),
      ).values(),
    ].sort((a: NeighborhoodInfo, b: NeighborhoodInfo) => a.name.localeCompare(b.name))

    cacheManager.set(cacheNeighborhoods, sendNeighborhoods, 7)

    return sendNeighborhoods as NeighborhoodInfo[]
  } catch (e) {
    console.error('Erro ao pegar bairros com Overpass: ', e)
    return []
  }
}

const fetchNeighborhoodOutline = async (
  neighborhoodToFetch: NeighborhoodInfo[],
  cityName: string,
): Promise<Map<string, google.maps.LatLngLiteral[][]>> => {
  const results = new Map<string, google.maps.LatLngLiteral[][]>()
  if (neighborhoodToFetch.length === 0) return results

  const IdsNom = neighborhoodToFetch.map((n) => `${n.type}${n.id}`).join(',')

  const url = `https://nominatim.openstreetmap.org/lookup?osm_ids=${IdsNom}&format=json&polygon_geojson=1&email=natanybraga@gmail.com`

  try {
    const response = await fetch(url)
    const data = await response.json()

    if (Array.isArray(data)) {
      data.forEach((item: any) => {
        const foundNeighborhood = neighborhoodToFetch.find((n) => n.id === item.osm_id)
        if (!foundNeighborhood) return
        const name = foundNeighborhood.name

        if (!item.geojson) return

        const geojson = item.geojson
        const paths: google.maps.LatLngLiteral[][] = []

        if (geojson.type === 'Polygon') {
          geojson.coordinates.forEach((ring: any) => {
            paths.push(ring.map(([lng, lat]: [number, number]) => ({ lat, lng })))
          })
        } else if (geojson.type === 'MultiPolygon') {
          geojson.coordinates.forEach((polygon: any) => {
            polygon.forEach((ring: any) => {
              paths.push(ring.map(([lng, lat]: [number, number]) => ({ lat, lng })))
            })
          })
        }
        if (paths.length > 0) {
          results.set(name, paths)

          cacheManager.set(`outline-${name}-${cityName}`, paths, 7)
        }
      })
    }
    return results
  } catch (e) {
    console.error('Erro no Nominatim Lookup: ', e)
    return results
  }
}

export const neighborhoodOutlines = async (
  map: google.maps.Map,
  neighborhoodNames: string[],
  cityName: string,
  fixedCamera: boolean = true,
): Promise<void> => {
  const currentNameSet = new Set(neighborhoodNames)

  for (const [name, polygon] of polygonsCleaner.entries()) {
    if (!currentNameSet.has(name)) {
      polygon.setMap(null)
      polygonsCleaner.delete(name)
    }
  }

  const allNeighborhoods = await fetchAllNeighborhoods(cityName)

  const missingNeighborhoods: NeighborhoodInfo[] = []
  const geometryToDraw = new Map<string, google.maps.LatLngLiteral[][]>()

  neighborhoodNames.forEach((name) => {
    if (polygonsCleaner.has(name)) return

    const cached = cacheManager.get<google.maps.LatLngLiteral[][]>(`outline-${name}-${cityName}`)
    if (cached) {
      geometryToDraw.set(name, cached)
    } else {
      const bInfo = allNeighborhoods.find((n) => n.name === name)
      if (bInfo) missingNeighborhoods.push(bInfo)
    }
  })

  if (missingNeighborhoods.length > 0) {
    //O Nominatim vai dividir em 50 blocos de bairros
    for (let i = 0; i < missingNeighborhoods.length; i += 50) {
      const chunk = missingNeighborhoods.slice(i, i + 50)
      const lookupResults = await fetchNeighborhoodOutline(chunk, cityName)

      lookupResults.forEach((paths, name) => {
        geometryToDraw.set(name, paths)
      })
      if (i + 50 < missingNeighborhoods.length) {
        await new Promise((resolve) => setTimeout(resolve, 1200))
      }
    }
  }

  const allBounds = new google.maps.LatLngBounds()
  let addedNewPolygon = false

  //Criar parametros para implementar funcionalidade de desligamento programado
  //EX: func(Local, programado, não-programado) -> valores podendo ser nulos

  geometryToDraw.forEach((paths, name) => {
    if (paths.length > 0) {
      const polygon = new google.maps.Polygon({
        paths: paths,
        strokeColor: '#FF4500',
        strokeOpacity: 0.5,
        strokeWeight: 2,
        fillColor: '#FF4500',
        fillOpacity: 0.35,
        map: map,
        zIndex: 15,
      })

      polygon.addListener('click', () => {
        window.dispatchEvent(
          new CustomEvent('map-neighborhood-clicked', {
            detail: { name: name, city: cityName },
          }),
        )
      })

      polygonsCleaner.set(name, polygon)
      addedNewPolygon = true

      paths.forEach((path) => {
        path.forEach((point) => allBounds.extend(point))
      })
    }
  })

  if (addedNewPolygon && fixedCamera) {
    map.fitBounds(allBounds, 50)
  }
}
export const findNeighborhoodCoords = (latlng: google.maps.LatLng): string | null => {
  for (const [name, polygon] of polygonsCleaner.entries()) {
    if (google.maps.geometry.poly.containsLocation(latlng, polygon)) return name
  }
  return null
}
