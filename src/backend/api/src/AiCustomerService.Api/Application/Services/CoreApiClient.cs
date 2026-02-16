namespace AiCustomerService.Api.Application.Services;

using AiCustomerService.Api.Application.Interfaces;

public sealed class CoreApiClient : ICoreApiClient
{
    private readonly HttpClient _httpClient;

    public CoreApiClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct = default)
    {
        return await _httpClient.SendAsync(request, ct);
    }
}
