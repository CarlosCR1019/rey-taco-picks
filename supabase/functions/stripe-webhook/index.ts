import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.7.1"
import Stripe from 'https://esm.sh/stripe@11.1.0?target=deno'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') as string, {
  apiVersion: '2022-11-15',
  httpClient: Stripe.createFetchHttpClient(),
})

const cryptoProvider = Stripe.createSubtleCryptoProvider()

serve(async (req) => {
  const signature = req.headers.get('Stripe-Signature')
  
  if (!signature) {
    return new Response('No signature provided', { status: 400 })
  }

  try {
    const body = await req.text()
    // Validar la firma criptográfica para evitar hackeos
    const event = await stripe.webhooks.constructEventAsync(
      body,
      signature,
      Deno.env.get('STRIPE_WEBHOOK_SECRET') as string,
      undefined,
      cryptoProvider
    )

    // Solo nos interesa cuando un pago de suscripción se ha completado
    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session
      const customerEmail = session.customer_details?.email

      if (customerEmail) {
        // Inicializar Supabase usando la llave maestra secreta
        const supabaseUrl = Deno.env.get('SUPABASE_URL') as string
        const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') as string
        
        const supabase = createClient(supabaseUrl, supabaseServiceRoleKey)

        // Buscar al usuario por email y actualizar su perfil a Premium
        const { error } = await supabase
          .from('profiles')
          .update({ is_premium: true })
          .eq('email', customerEmail)

        if (error) {
          console.error('Error actualizando perfil en Supabase:', error)
          return new Response('Database error', { status: 500 })
        }

        console.log(`✅ ¡Pago exitoso! Acceso premium otorgado a: ${customerEmail}`)
      }
    }

    return new Response(JSON.stringify({ received: true }), { status: 200 })
  } catch (err: any) {
    console.error('Error procesando webhook:', err.message)
    return new Response(err.message, { status: 400 })
  }
})
