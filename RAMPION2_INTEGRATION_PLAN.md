# JereChat Rampion 2 Integration Plan

## Overview
Integrate the PyTorch-based JereChat Rampion 2 model into the Streamlit website with A/B testing capabilities and Supabase feedback tracking.

## Current State
- **JereChat Rampion 2**: PyTorch seq2seq model with encoder-decoder architecture, GRU + Luong attention, trained checkpoints available
- **jerechat website**: Streamlit app with invitation system, currently uses external API, has Supabase feedback integration

## Phase 1: Model Packaging & API Layer

### 1.1 Create Model Wrapper Module
**File**: `jerechat/rampion2_model.py`
- Load PyTorch model from checkpoint
- Implement inference interface
- Handle text normalization and tokenization
- Return decoded responses
- Support batch processing for efficiency

**Dependencies**:
- torch
- Add to requirements.txt

### 1.2 Update Requirements
**File**: `requirements.txt`
- Add: `torch>=2.0.0`
- Keep: `streamlit`, `supabase==2.0.0`

---

## Phase 2: A/B Testing Infrastructure

### 2.1 A/B Testing Configuration
**File**: `jerechat/ab_testing.py`
- Implement model selection logic (50/50 split initially)
- Track which model version each user is assigned to
- Store assignment in session state
- Support configurable split ratios

### 2.2 Update Database Schema
**Action**: Add columns to Supabase `feedback` table
- `model_version`: "1.5pro" or "rampion2"
- `model_assignment_timestamp`: When user was assigned to model
- `response_time`: Time taken to generate response

---

## Phase 3: Streamlit Integration

### 3.1 Update Model Selection UI
**File**: `streamlit_app.py`
- Add model pills: "1.5pro" and "DeepThink (Rampion 2)"
- Show active model in sidebar
- Allow manual override (for testing)

### 3.2 Integrate Rampion 2 Inference
**File**: `streamlit_app.py`
- Import rampion2_model module
- Update `get_response()` to route to correct model
- Add model version tracking in session state
- Measure and log response times

### 3.3 Update Feedback Collection
**File**: `streamlit_app.py`
- Pass model version to feedback
- Include response time metrics
- Track A/B group assignment

---

## Phase 4: Deployment & Optimization

### 4.1 Model Loading Optimization
- Cache model in session state (load once per session)
- Implement lazy loading
- Handle model loading errors gracefully

### 4.2 Environment Configuration
**File**: `.streamlit/secrets.toml`
- Add model path configuration
- Add A/B testing split ratio
- Keep existing Supabase and invitation configs

### 4.3 Error Handling
- Fallback to current API if Rampion 2 fails
- Log errors for debugging
- Show user-friendly error messages

---

## Phase 5: Monitoring & Analytics

### 5.1 Dashboard Updates
**File**: `streamlit_app.py` (admin sidebar)
- Show model usage statistics
- Display feedback comparison
- Response time metrics
- A/B test results

### 5.2 Database Queries
**File**: `database.py`
- Add `get_model_feedback_stats(model_version)`
- Add `get_ab_test_results()`
- Add `get_response_time_stats(model_version)`

---

## Phase 6: Testing & Validation

### 6.1 Unit Tests
- Test model loading
- Test inference with sample inputs
- Test A/B assignment logic
- Test feedback saving with model version

### 6.2 Integration Tests
- Test full chat flow with both models
- Test feedback submission
- Test session persistence
- Test error handling

### 6.3 Performance Testing
- Measure response times
- Test concurrent users
- Monitor memory usage

---

## Phase 7: Documentation

### 7.1 Update README
**File**: `README.md`
- Document A/B testing setup
- Explain model versions
- Add troubleshooting section

### 7.2 Create Deployment Guide
**File**: `DEPLOYMENT.md`
- Model checkpoint placement
- Environment setup
- Supabase schema updates
- Deployment steps

---

## Implementation Order

1. **Phase 1**: Create model wrapper and update requirements
2. **Phase 2**: Build A/B testing infrastructure
3. **Phase 3**: Integrate into Streamlit app
4. **Phase 4**: Optimize and configure
5. **Phase 5**: Add monitoring
6. **Phase 6**: Test thoroughly
7. **Phase 7**: Document everything

---

## Success Criteria

- [ ] Both models accessible via UI
- [ ] A/B testing randomly assigns users
- [ ] Feedback tracked with model version
- [ ] Response times measured and stored
- [ ] Dashboard shows comparative stats
- [ ] Error handling works gracefully
- [ ] Documentation complete

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Model loading slow | Cache in session, show loading indicator |
| PyTorch memory issues | Implement cleanup, monitor usage |
| A/B assignment bias | Use proper randomization, track assignments |
| Feedback data inconsistency | Validate data before saving |
| API fallback needed | Implement graceful degradation |

---

## Future Enhancements

- Multi-arm bandit testing (dynamic allocation)
- Model versioning system
- Automated model retraining pipeline
- Real-time A/B test statistics
- User segmentation for targeted testing
