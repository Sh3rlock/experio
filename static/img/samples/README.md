# Sample offer images

Each JPEG is tied to one demo offer via `image_key` in `seed_sample_offers.py`.  
Sources are **verified Pexels photo IDs** (checked for color/content — not grayscale mismatches).

| File | Offer | Pexels ID |
|------|-------|-----------|
| `arboretum.jpg` | Folly Arboretum | 2255935 |
| `vintage-cars.jpg` | Classic Car Exhibition | 170811 |
| `supercar.jpg` | Supercar Driving Experience | 2444429 |
| `beach.jpg` | Summer Beach Day | 457882 |
| `balloon.jpg` | Hot Air Balloon Flight | **670061** |
| `city-break.jpg` | Transylvania City Break | 1179225 |
| `spa.jpg` | Luxury Spa Day | 3757952 |
| `restaurant.jpg` | Gourmet Dinner | 941861 |
| `brunch.jpg` | Weekend Brunch | 1527603 |
| `massage.jpg` | Therapeutic Massage | 269077 |
| `beauty.jpg` | Premium Facial | 3997985 |
| `adventure.jpg` | Adventure Park | 1371667 |
| `escape-room.jpg` | Escape Room | 3945313 |
| `fitness.jpg` | Fitness Bootcamp | 2261476 |
| `wine-course.jpg` | Wine Tasting Workshop | 6029684 |
| `gift-card.jpg` | Spa Gift Card | 1303080 |

Photos from [Pexels](https://www.pexels.com) (free license).

Refresh and re-attach to offers (includes automatic color check):

```bash
python manage.py seed_sample_offers --fetch-images
python manage.py seed_sample_offers
```
