import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import './ActionsPage.css';

const defaultNewAction = {
  action_type: 'BUY',
  symbol: '',
  quantity: '',
  amount_usd: '',
  trigger_type: 'price_above',
  trigger_params: { threshold: '' },
  use_valid_window: false,
  valid_until: '',
  cooldown_seconds: '',
  max_executions: 1,
  notes: ''
};

const ActionsPage = ({ isMobile, toggleMobileNav }) => {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [newAction, setNewAction] = useState(defaultNewAction);
  const [saving, setSaving] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredActions = useMemo(() => {
    if (filterStatus === 'all') return actions;
    return actions.filter(a => a.status === filterStatus);
  }, [actions, filterStatus]);

  const activeActions = useMemo(() => actions.filter(a => a.status === 'active' || a.status === 'paused'), [actions]);
  const pastActions = useMemo(() => actions.filter(a => ['completed','cancelled','failed'].includes(a.status)), [actions]);

  const fetchActions = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (filterStatus !== 'all') params.status = filterStatus;
      const res = await axios.get('/actions', { params });
      setActions(res.data.actions || []);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load actions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterStatus]);

  const resetModal = () => {
    setNewAction(defaultNewAction);
    setShowModal(false);
    setSaving(false);
    setError('');
  };

  const handleCreate = async () => {
    setSaving(true);
    setError('');
    try {
      const payload = { ...newAction };
      if (!payload.symbol) delete payload.symbol;
      if (!payload.quantity) delete payload.quantity;
      if (!payload.amount_usd) delete payload.amount_usd;
      if (!payload.cooldown_seconds) delete payload.cooldown_seconds;
      if (!payload.valid_until) delete payload.valid_until;
      if (!payload.notes) delete payload.notes;
      // Cast numbers
      if (payload.quantity) payload.quantity = parseFloat(payload.quantity);
      if (payload.amount_usd) payload.amount_usd = parseFloat(payload.amount_usd);
      if (payload.cooldown_seconds) payload.cooldown_seconds = parseInt(payload.cooldown_seconds, 10);
      if (payload.trigger_type.startsWith('price') && payload.trigger_params?.threshold) {
        payload.trigger_params.threshold = parseFloat(payload.trigger_params.threshold);
      }
      const res = await axios.post('/actions', payload);
      if (res.data) {
        await fetchActions();
        resetModal();
      }
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to create action');
    } finally {
      setSaving(false);
    }
  };

  const handlePauseResume = async (action, targetStatus) => {
    try {
      await axios.patch(`/actions/${action.id}`, { status: targetStatus });
      fetchActions();
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to update action');
    }
  };

  const handleDelete = async (action) => {
    try {
      await axios.delete(`/actions/${action.id}`);
      fetchActions();
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to delete action');
    }
  };

  const renderTrigger = (a) => {
    const t = (a.trigger_type || '').replace('_', ' ');
    if (a.trigger_type === 'price_above' || a.trigger_type === 'price_below') {
      return `${t} ${a.trigger_params?.threshold}`;
    }
    if (a.trigger_type === 'change_pct') {
      const dir = a.trigger_params?.direction || 'up';
      return `${dir} ${a.trigger_params?.change}%`;
    }
    if (a.trigger_type === 'time_of_day') {
      return `${a.trigger_params?.start || ''} - ${a.trigger_params?.end || ''}`;
    }
    return t;
  };

  return (
    <div className="actions-page">
      <div className="page-header">
        <div className="title-group">
          <h1>Actions</h1>
          <p className="subtitle">Automate trades and alerts when your conditions are met.</p>
        </div>
        <div className="header-actions">
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="filter-select">
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button className="primary-btn" onClick={() => setShowModal(true)}>Add Action</button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading actions...</div>
      ) : (
        <>
          <div className="section">
            <div className="section-header">Active</div>
            <div className="actions-table-wrapper">
              <table className="actions-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Symbol</th>
                    <th>Trigger</th>
                    <th>Executions</th>
                    <th>Last Triggered</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {activeActions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="empty-cell">
                        No active actions. Click "Add Action" to create your first rule.
                      </td>
                    </tr>
                  ) : activeActions.map(a => (
                    <tr key={a.id}>
                      <td><span className={`status-chip ${a.status}`}>{a.status}</span></td>
                      <td>{a.action_type}</td>
                      <td>{a.symbol || '-'}</td>
                      <td>{renderTrigger(a)}</td>
                      <td>{a.executions_count || 0}/{a.max_executions || 1}</td>
                      <td>{a.last_triggered_at ? new Date(a.last_triggered_at).toLocaleString() : '-'}</td>
                      <td className="row-actions">
                        {a.status === 'active' ? (
                          <button className="secondary-btn" onClick={() => handlePauseResume(a, 'paused')}>Pause</button>
                        ) : a.status === 'paused' ? (
                          <button className="secondary-btn" onClick={() => handlePauseResume(a, 'active')}>Resume</button>
                        ) : null}
                        <button className="danger-btn" onClick={() => handleDelete(a)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="section">
            <div className="section-header">Past</div>
            <div className="actions-table-wrapper">
              <table className="actions-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Symbol</th>
                    <th>Trigger</th>
                    <th>Executions</th>
                    <th>Last Triggered</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pastActions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="empty-cell">No past actions.</td>
                    </tr>
                  ) : pastActions.map(a => (
                    <tr key={a.id}>
                      <td><span className={`status-chip ${a.status}`}>{a.status}</span></td>
                      <td>{a.action_type}</td>
                      <td>{a.symbol || '-'}</td>
                      <td>{renderTrigger(a)}</td>
                      <td>{a.executions_count || 0}/{a.max_executions || 1}</td>
                      <td>{a.last_triggered_at ? new Date(a.last_triggered_at).toLocaleString() : '-'}</td>
                      <td className="row-actions">
                        <button className="secondary-btn" onClick={() => setNewAction({
                          ...defaultNewAction,
                          action_type: a.action_type,
                          symbol: a.symbol || '',
                          trigger_type: a.trigger_type,
                          trigger_params: a.trigger_params || {},
                        }) & setShowModal(true)}>Re-add</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-backdrop" onClick={resetModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Action</h2>
            </div>
            <div className="modal-body">
              <div className="form-row">
                <label>Action Type <span className="req">required</span></label>
                <select value={newAction.action_type} onChange={e => setNewAction({ ...newAction, action_type: e.target.value })}>
                  <option value="BUY">Buy</option>
                  <option value="SELL">Sell</option>
                  <option value="NOTIFY">Notify</option>
                </select>
              </div>
              <div className="form-row">
                <label>Symbol <span className="opt">optional for Notify</span></label>
                <input placeholder="AAPL" value={newAction.symbol} onChange={e => setNewAction({ ...newAction, symbol: e.target.value.toUpperCase() })} />
              </div>
              <div className="form-grid">
                <div className="form-row">
                  <label>Quantity <span className="opt">optional (use Amount instead)</span></label>
                  <input type="number" step="0.0001" value={newAction.quantity} onChange={e => setNewAction({ ...newAction, quantity: e.target.value })} />
                </div>
                <div className="form-row">
                  <label>Amount (USD) <span className="opt">optional (use Quantity instead)</span></label>
                  <input type="number" step="0.01" value={newAction.amount_usd} onChange={e => setNewAction({ ...newAction, amount_usd: e.target.value })} />
                </div>
              </div>
              <div className="form-row">
                <label>Trigger Type <span className="req">required</span></label>
                <select value={newAction.trigger_type} onChange={e => setNewAction({ ...newAction, trigger_type: e.target.value, trigger_params: {} })}>
                  <option value="price_above">Price above</option>
                  <option value="price_below">Price below</option>
                  <option value="change_pct">Percent change</option>
                  <option value="time_of_day">Time of day</option>
                </select>
              </div>

              {newAction.trigger_type === 'price_above' || newAction.trigger_type === 'price_below' ? (
                <div className="form-row">
                  <label>Threshold Price <span className="req">required</span></label>
                  <input type="number" step="0.01" value={newAction.trigger_params.threshold || ''} onChange={e => setNewAction({ ...newAction, trigger_params: { ...newAction.trigger_params, threshold: e.target.value } })} />
                </div>
              ) : null}

              {newAction.trigger_type === 'change_pct' ? (
                <div className="form-grid">
                  <div className="form-row">
                    <label>Direction</label>
                    <select value={newAction.trigger_params.direction || 'up'} onChange={e => setNewAction({ ...newAction, trigger_params: { ...newAction.trigger_params, direction: e.target.value } })}>
                      <option value="up">Up</option>
                      <option value="down">Down</option>
                    </select>
                  </div>
                  <div className="form-row">
                    <label>Percent <span className="req">required</span></label>
                    <input type="number" step="0.01" value={newAction.trigger_params.change || ''} onChange={e => setNewAction({ ...newAction, trigger_params: { ...newAction.trigger_params, change: e.target.value } })} />
                  </div>
                </div>
              ) : null}

              {newAction.trigger_type === 'time_of_day' ? (
                <div className="form-grid">
                  <div className="form-row">
                    <label>Start (UTC)</label>
                    <input type="time" value={newAction.trigger_params.start || ''} onChange={e => setNewAction({ ...newAction, trigger_params: { ...newAction.trigger_params, start: e.target.value } })} />
                  </div>
                  <div className="form-row">
                    <label>End (UTC)</label>
                    <input type="time" value={newAction.trigger_params.end || ''} onChange={e => setNewAction({ ...newAction, trigger_params: { ...newAction.trigger_params, end: e.target.value } })} />
                  </div>
                </div>
              ) : null}

              <div className="form-grid">
                <div className="form-row">
                  <label>Max Executions</label>
                  <input type="number" min="1" value={newAction.max_executions} onChange={e => setNewAction({ ...newAction, max_executions: parseInt(e.target.value || '1', 10) })} />
                </div>
                <div className="form-row">
                  <label>Cooldown (sec)</label>
                  <input type="number" min="0" value={newAction.cooldown_seconds} onChange={e => setNewAction({ ...newAction, cooldown_seconds: e.target.value })} />
                </div>
              </div>

              <div className="form-row">
                <label>Validity Window <span className="opt">optional</span></label>
                <div style={{display:'flex', alignItems:'center', gap: '12px'}}>
                  <label style={{display:'flex', alignItems:'center', gap:'8px'}}>
                    <input type="checkbox" checked={newAction.use_valid_window} onChange={e => setNewAction({ ...newAction, use_valid_window: e.target.checked })} />
                    Enable valid until
                  </label>
                  {newAction.use_valid_window && (
                    <input type="datetime-local" value={newAction.valid_until} onChange={e => setNewAction({ ...newAction, valid_until: e.target.value })} />
                  )}
                </div>
                <div className="help-text">If enabled, the action will be marked completed once the time is reached.</div>
              </div>

              <div className="form-row">
                <label>Notes <span className="opt">optional</span></label>
                <textarea rows={3} value={newAction.notes} onChange={e => setNewAction({ ...newAction, notes: e.target.value })} />
              </div>
            </div>
            <div className="modal-footer">
              <button className="secondary-btn" onClick={resetModal} disabled={saving}>Cancel</button>
              <button className="primary-btn" onClick={handleCreate} disabled={saving}>
                {saving ? 'Creating...' : 'Create Action'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionsPage;


