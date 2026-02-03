package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestSuccess(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	data := map[string]string{"key": "value"}
	Success(c, data)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 0 {
		t.Errorf("Expected code 0, got %d", resp.Code)
	}
	if resp.Message != "success" {
		t.Errorf("Expected message 'success', got %s", resp.Message)
	}
}

func TestSuccessWithMessage(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	SuccessWithMessage(c, "操作成功", nil)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Message != "操作成功" {
		t.Errorf("Expected message '操作成功', got %s", resp.Message)
	}
}

func TestSuccessPage(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	list := []string{"item1", "item2"}
	SuccessPage(c, list, 100, 1, 10)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 0 {
		t.Errorf("Expected code 0, got %d", resp.Code)
	}

	// 检查分页数据
	data, ok := resp.Data.(map[string]interface{})
	if !ok {
		t.Fatal("Data should be a map")
	}

	if data["total"].(float64) != 100 {
		t.Errorf("Expected total 100, got %v", data["total"])
	}
	if data["page"].(float64) != 1 {
		t.Errorf("Expected page 1, got %v", data["page"])
	}
	if data["page_size"].(float64) != 10 {
		t.Errorf("Expected page_size 10, got %v", data["page_size"])
	}
}

func TestError(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	Error(c, 1001, "自定义错误")

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 1001 {
		t.Errorf("Expected code 1001, got %d", resp.Code)
	}
	if resp.Message != "自定义错误" {
		t.Errorf("Expected message '自定义错误', got %s", resp.Message)
	}
}

func TestErrorWithStatus(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	ErrorWithStatus(c, http.StatusInternalServerError, 500, "服务器错误")

	if w.Code != http.StatusInternalServerError {
		t.Errorf("Expected status %d, got %d", http.StatusInternalServerError, w.Code)
	}
}

func TestBadRequest(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	BadRequest(c, "参数错误")

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 400 {
		t.Errorf("Expected code 400, got %d", resp.Code)
	}
}

func TestUnauthorized(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	Unauthorized(c, "未授权")

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 401 {
		t.Errorf("Expected code 401, got %d", resp.Code)
	}
}

func TestForbidden(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	Forbidden(c, "禁止访问")

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status %d, got %d", http.StatusForbidden, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 403 {
		t.Errorf("Expected code 403, got %d", resp.Code)
	}
}

func TestNotFound(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	NotFound(c, "资源不存在")

	if w.Code != http.StatusNotFound {
		t.Errorf("Expected status %d, got %d", http.StatusNotFound, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 404 {
		t.Errorf("Expected code 404, got %d", resp.Code)
	}
}

func TestInternalError(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	InternalError(c, "内部错误")

	if w.Code != http.StatusInternalServerError {
		t.Errorf("Expected status %d, got %d", http.StatusInternalServerError, w.Code)
	}

	var resp Response
	json.Unmarshal(w.Body.Bytes(), &resp)

	if resp.Code != 500 {
		t.Errorf("Expected code 500, got %d", resp.Code)
	}
}

func TestResponse_Structure(t *testing.T) {
	resp := Response{
		Code:    0,
		Message: "success",
		Data:    map[string]string{"id": "1"},
	}

	if resp.Code != 0 {
		t.Errorf("Code = %d, want 0", resp.Code)
	}
	if resp.Message != "success" {
		t.Errorf("Message = %s, want success", resp.Message)
	}
	if resp.Data == nil {
		t.Error("Data should not be nil")
	}
}

func TestPageResponse_Structure(t *testing.T) {
	resp := PageResponse{
		List:     []string{"a", "b", "c"},
		Total:    100,
		Page:     1,
		PageSize: 10,
	}

	if resp.Total != 100 {
		t.Errorf("Total = %d, want 100", resp.Total)
	}
	if resp.Page != 1 {
		t.Errorf("Page = %d, want 1", resp.Page)
	}
	if resp.PageSize != 10 {
		t.Errorf("PageSize = %d, want 10", resp.PageSize)
	}
}
