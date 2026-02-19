using AiCustomerService.Api.Application.Interfaces;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;

namespace AiCustomerService.Api.Tests;

/// <summary>
/// WebApplicationFactory that replaces ICoreApiClient with an NSubstitute mock so all
/// endpoint tests are fully isolated from the real Core service.
/// Each test class gets its own instance (via IClassFixture) with a fresh mock.
/// </summary>
public sealed class ApiTestFactory : WebApplicationFactory<Program>
{
    /// <summary>
    /// NSubstitute mock of the Core API client.  Configure return values before
    /// calling any endpoint under test.
    /// </summary>
    public ICoreApiClient CoreApiClient { get; } = Substitute.For<ICoreApiClient>();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Test");

        builder.ConfigureServices(services =>
        {
            // Remove every existing registration for ICoreApiClient.
            // AddHttpClient<ICoreApiClient, CoreApiClient> registers a factory
            // delegate whose ServiceType is ICoreApiClient.
            var descriptors = services
                .Where(d => d.ServiceType == typeof(ICoreApiClient))
                .ToList();

            foreach (var descriptor in descriptors)
            {
                services.Remove(descriptor);
            }

            // Register the NSubstitute mock as a singleton so all injected endpoints
            // receive the same instance that the test has configured.
            services.AddSingleton(CoreApiClient);
        });
    }

    /// <summary>
    /// Clears NSubstitute's received call records on the mock so that
    /// <c>DidNotReceive()</c> assertions work correctly across tests
    /// within the same test class.  Call this at the start of each test.
    /// </summary>
    public void ResetReceivedCalls()
    {
        CoreApiClient.ClearReceivedCalls();
    }
}
