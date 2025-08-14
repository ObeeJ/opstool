package api

import (
	"encoding/json"
	"net/http"
	"opstool/pkg/gdpr"
	"time"
)

type GDPRHandler struct {
	manager *gdpr.GDPRManager
}

func NewGDPRHandler() *GDPRHandler {
	return &GDPRHandler{
		manager: gdpr.NewGDPRManager(),
	}
}

// HandleDataDeletion processes right to be forgotten requests
func (h *GDPRHandler) HandleDataDeletion(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-ID")
	if userID == "" {
		http.Error(w, "User ID required", http.StatusBadRequest)
		return
	}

	err := h.manager.RequestDataDeletion(userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "deletion_requested",
		"user_id": userID,
	})
}

// HandleDataExport processes data portability requests
func (h *GDPRHandler) HandleDataExport(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-ID")
	if userID == "" {
		http.Error(w, "User ID required", http.StatusBadRequest)
		return
	}

	data, err := h.manager.ExportUserData(userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Content-Disposition", "attachment; filename=user_data_export.json")
	w.Write(data)
}

// HandleConsentUpdate processes consent updates
func (h *GDPRHandler) HandleConsentUpdate(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UserID  string `json:"user_id"`
		Consent bool   `json:"consent"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err := h.manager.UpdateConsent(req.UserID, req.Consent)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "consent_updated",
		"user_id":   req.UserID,
		"consent":   req.Consent,
		"timestamp": time.Now(),
	})
}
