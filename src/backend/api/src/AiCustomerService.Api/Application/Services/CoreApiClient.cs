namespace AiCustomerService.Api.Application.Services;

using System.Net.Http.Json;
using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;

public sealed class CoreApiClient : ICoreApiClient
{
    private readonly HttpClient _httpClient;

    public CoreApiClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<QueryResponseDto> QueryAsync(QueryRequestDto request, CancellationToken ct = default)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/v1/query", request, ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<QueryResponseDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<List<KnowledgeBaseDto>> ListKnowledgeBasesAsync(CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync("/api/v1/knowledge-bases", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<KnowledgeBaseDto>>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<KnowledgeBaseDto> CreateKnowledgeBaseAsync(CreateKnowledgeBaseRequestDto request, CancellationToken ct = default)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/v1/knowledge-bases", request, ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<KnowledgeBaseDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<KnowledgeBaseDto> GetKnowledgeBaseAsync(string id, CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync($"/api/v1/knowledge-bases/{id}", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<KnowledgeBaseDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task DeleteKnowledgeBaseAsync(string id, CancellationToken ct = default)
    {
        var response = await _httpClient.DeleteAsync($"/api/v1/knowledge-bases/{id}", ct);
        response.EnsureSuccessStatusCode();
    }

    public async Task<List<DocumentDto>> ListDocumentsAsync(string kbId, CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync($"/api/v1/knowledge-bases/{kbId}/documents", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<DocumentDto>>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<DocumentDto> UploadDocumentAsync(string kbId, Stream file, string filename, CancellationToken ct = default)
    {
        using var content = new MultipartFormDataContent();
        using var fileContent = new StreamContent(file);
        fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
        content.Add(fileContent, "file", filename);

        var response = await _httpClient.PostAsync($"/api/v1/knowledge-bases/{kbId}/documents", content, ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<DocumentDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task DeleteDocumentAsync(string kbId, string docId, CancellationToken ct = default)
    {
        var response = await _httpClient.DeleteAsync($"/api/v1/knowledge-bases/{kbId}/documents/{docId}", ct);
        response.EnsureSuccessStatusCode();
    }

    public async Task TriggerIndexingAsync(string kbId, CancellationToken ct = default)
    {
        var response = await _httpClient.PostAsync($"/api/v1/knowledge-bases/{kbId}/index", null, ct);
        response.EnsureSuccessStatusCode();
    }

    public async Task<List<InteractionDto>> ListInteractionsAsync(CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync("/api/v1/interactions", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<List<InteractionDto>>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<InteractionDto> GetInteractionAsync(string id, CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync($"/api/v1/interactions/{id}", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<InteractionDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }

    public async Task<DashboardStatsDto> GetDashboardStatsAsync(CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync("/api/v1/dashboard/stats", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<DashboardStatsDto>(ct)
            ?? throw new InvalidOperationException("Null response from Core API");
    }
}
