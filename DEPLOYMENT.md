# JereChat Rampion 2 Deployment Guide

## Overview
This guide covers deploying the JereChat Rampion 2 integration with A/B testing and Supabase feedback tracking.

## Prerequisites

1. **Model Checkpoint**: Place the trained Rampion 2 model checkpoint
2. **Supabase Database**: Update schema to support A/B testing
3. **Python Dependencies**: Install required packages

## Step 1: Place Model Checkpoint

Copy your Rampion 2 model checkpoint to the website directory:

```bash
# From JereChat Rampion 2 directory
cp "data/save/cb_model/corpus/2-2_500/2000_checkpoint.tar" /path/to/jerechat/data/save/cb_model/corpus/2-2_500/
```

Or update the path in `.streamlit/secrets.toml`:
```toml
rampion2_checkpoint_path = "/your/custom/path/to/checkpoint.tar"
```

## Step 2: Update Supabase Schema

Add the following columns to your `feedback` table:

```sql
ALTER TABLE feedback 
ADD COLUMN model_version TEXT,
ADD COLUMN model_assignment_timestamp TIMESTAMP WITH TIME ZONE,
ADD COLUMN response_time FLOAT;

-- Create index for faster queries
CREATE INDEX idx_feedback_model_version ON feedback(model_version);
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `streamlit`
- `supabase==2.0.0`
- `torch>=2.0.0`

## Step 4: Configure Environment

Update `.streamlit/secrets.toml`:

```toml
# Existing Supabase config
supabase_url = "your_supabase_url"
supabase_key = "your_supabase_key"

# Rampion 2 Model Configuration
rampion2_checkpoint_path = "data/save/cb_model/corpus/2-2_500/2000_checkpoint.tar"
ab_test_split_ratio = 0.5  # 50/50 split between models

# Invitation codes
[[invitation_codes]]
code_number = "123456"
code_notes = "Initial test code"
code_expiry_date = "2025-12-31"
```

## Step 5: Run the Application

```bash
streamlit run streamlit_app.py
```

## A/B Testing How It Works

1. **Random Assignment**: Each new user is randomly assigned to either "1.5pro" or "rampion2" model
2. **Session Persistence**: Assignment persists for the user's session
3. **Manual Override**: Use `ab_testing.set_model_version()` for testing
4. **Feedback Tracking**: All feedback includes model version and response time

## Monitoring Dashboard

Access the A/B Test Dashboard in the sidebar to see:
- Your assigned model version
- Good/bad feedback counts per model
- Average response times per model

## Troubleshooting

### Model Loading Fails
- Check checkpoint path in secrets.toml
- Verify checkpoint file exists and is readable
- Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`

### Fallback to 1.5pro
- If Rampion 2 fails to load, app automatically falls back to 1.5pro
- Check browser console for error messages
- Verify model checkpoint compatibility

### Supabase Errors
- Verify Supabase credentials in secrets.toml
- Check database schema has required columns
- Test connection: `python -c "from database import _init_supabase; print(_init_supabase())"`

### Response Time Issues
- Rampion 2 runs locally, should be faster than API
- Check system resources (CPU/GPU)
- Monitor memory usage during inference

## Testing

### Test A/B Assignment
```python
from jerechat import ab_testing
ab_testing.reset_assignment()  # Clear assignment
version = ab_testing.assign_model_version()  # Get new assignment
print(f"Assigned to: {version}")
```

### Test Both Models
```python
from jerechat import ab_testing
ab_testing.set_model_version("1.5pro")  # Test 1.5pro
ab_testing.set_model_version("rampion2")  # Test Rampion 2
```

### Test Database Queries
```python
from database import get_ab_test_results, get_response_time_stats
print(get_ab_test_results())
print(get_response_time_stats())
```

## Performance Considerations

- **Model Caching**: Rampion 2 loads once per session and stays cached
- **Memory Usage**: ~500MB for model in memory
- **Response Time**: Typically <1 second for local inference
- **Concurrent Users**: Each user session loads model independently

## Security Notes

- Never commit `.streamlit/secrets.toml` to version control
- Keep Supabase keys secure
- Monitor feedback for abuse patterns
- Consider rate limiting for production

## Next Steps

1. Place model checkpoint
2. Update Supabase schema
3. Test locally
4. Deploy to production
5. Monitor A/B test results
6. Analyze feedback data

## Support

For issues or questions:
- Check browser console for errors
- Review Streamlit logs
- Verify all configuration files
- Test database connectivity
