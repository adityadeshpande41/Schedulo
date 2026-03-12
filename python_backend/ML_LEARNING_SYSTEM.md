# ML Learning System

## Overview

Schedulo uses machine learning to learn your scheduling preferences over time. The system gets smarter with each meeting you book or reject.

## How It Works

### 1. Data Collection

Every time you interact with the system, we collect data:

- **When you book a slot**: Saved as `was_accepted=True` in `historical_meetings` table
- **When you reject a slot**: Saved as `was_accepted=False` 
- **Data captured**:
  - Time of day (hour)
  - Day of week
  - Meeting type
  - Duration
  - Whether it was rescheduled or cancelled

### 2. ML Model Training

The system uses two ML models:

- **Random Forest Classifier**: Predicts if you'll accept a proposed time slot
- **Gradient Boosting Classifier**: Predicts if you'll reschedule existing meetings

**Training triggers**:
- Initial training: After 20 historical meetings
- Retraining: Every 10 meetings after that (30, 40, 50, etc.)

### 3. Prediction & Scoring

When finding meeting slots, the personal agent:

1. Loads your historical meeting data
2. Trains/updates the ML model if needed
3. For each potential slot:
   - Predicts acceptance probability (0-1)
   - Checks calendar conflicts
   - Evaluates learned preferences
   - Assigns confidence score

**Result**: Each slot gets a different score based on YOUR learned patterns!

### 4. Continuous Learning

The system learns from:
- ✅ Accepted meetings → Reinforces good patterns
- ❌ Rejected meetings → Learns what to avoid
- 🔄 Rescheduled meetings → Understands flexibility

## Current Status

✅ **Data Collection**: Implemented in `/api/schedule/slots/{id}/confirm` and `/reject`
✅ **ML Models**: Random Forest + Gradient Boosting in `ml_behavior_model.py`
✅ **Training Logic**: Personal agent trains when sufficient data exists
✅ **Prediction Integration**: Personal agent uses ML predictions for scoring
✅ **Seed Data**: 30 historical meetings seeded for initial training

## Learned Patterns

The system learns:

- **Time preferences**: "Prefers 10am over 4pm"
- **Day preferences**: "More flexible on Tuesdays"
- **Meeting type patterns**: "Prefers client calls in afternoons"
- **Reschedule likelihood**: "Willing to move internal meetings for client calls"

## Testing the System

1. **Check training data**:
   ```sql
   SELECT COUNT(*) FROM historical_meetings WHERE user_id = 'u1';
   ```

2. **Book meetings**: Accept/reject different time slots
3. **Watch scores change**: After 20+ meetings, scores will vary based on your patterns
4. **Check model status**: Look for "ML: True" in agent messages

## Future Enhancements

- [ ] Add user feedback reasons ("too early", "conflicts with lunch")
- [ ] Learn from meeting outcomes (was it productive?)
- [ ] Cross-user pattern learning (anonymized)
- [ ] Seasonal pattern detection (different preferences in summer/winter)
- [ ] Meeting type clustering (discover new meeting categories)
