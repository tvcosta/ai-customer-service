namespace AiCustomerService.Api.Application.Interfaces;

public interface ICoreApiClient
{
    Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct = default);
}
