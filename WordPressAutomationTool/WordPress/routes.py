from routes_progress import login_required
from routes_progress import app


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')


@app.route('/json/')
def serve_json():
    """Serve JSON data for generate_content.html"""
    return jsonify({})


@app.route('/wordpress_installation', methods=['GET', 'POST'])
@login_required
def wordpress_installation():
    if request.method == 'POST':
        wp_install = WordPressInstallation(
            server_id=current_user.server_connections[-1].id,
            site_url=request.form['site_url'],
            admin_username=request.form['admin_username'],
            admin_password=request.form['admin_password'],
            admin_email=request.form['admin_email'],
            site_title=request.form['site_title'])
        db.session.add(wp_install)
        db.session.commit()
        return redirect(url_for('website_category'))
    return render_template('wordpress_installation.html')


from flask import render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
import uuid
import json


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


from models import User, ServerConnection, WordPressInstallation, WebsiteCategory, Theme, SubscriptionPlan, ChatMessage, db
from datetime import datetime
import stripe
import os
import logging
import traceback

logger = logging.getLogger(__name__)

# Configure Stripe
flask_secret_key = os.getenv("FLASK_SECRET_KEY")
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
stripe.api_version = '2024-04-10'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin/reactivate_user/<int:user_id>', methods=['POST'])
@login_required
def reactivate_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'active'
            db.session.commit()
            return jsonify({'message': 'User reactivated successfully'})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error reactivating user: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/suspend_user/<int:user_id>', methods=['POST'])
@login_required
def suspend_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'suspended'
            db.session.commit()
            return jsonify({'message': 'User suspended successfully'})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error suspending user: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/terminate_subscription/<int:user_id>', methods=['POST'])
@login_required
def terminate_subscription(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        subscription = SubscriptionPlan.query.filter_by(
            user_id=user_id, status='active').first()
        if subscription:
            subscription.status = 'terminated'
            db.session.commit()
            return jsonify({'message': 'Subscription terminated successfully'})
        return jsonify({'error': 'No active subscription found'}), 404
    except Exception as e:
        logger.error(f"Error terminating subscription: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        admin_secret_key = request.form.get('admin_secret_key')
        email = request.form.get('email')
        password = request.form.get('password')

        if admin_secret_key != os.environ.get('ADMIN_SECRET_KEY'):
            flash('Invalid admin secret key')
            return render_template('admin_register.html')

        user = User(email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login', admin=True))

    return render_template('admin_register.html')


@app.route('/connect_server', methods=['GET', 'POST'])
@login_required
def connect_server():
    if request.method == 'POST':
        server = ServerConnection(
            user_id=current_user.id,
            domain_name=request.form['domain'],
            cpanel_username=request.form['cpanel_username'],
            cpanel_password=request.form['cpanel_password'],
            cpanel_api_key=request.form.get('cpanel_api_key'),
            softaculous_api_key=request.form.get('softaculous_api_key'),
            ssh_details=request.form.get('ssh_details'),
            installation_method=request.form.get('installation_method', 'api'))
        db.session.add(server)
        db.session.commit()
        return redirect(url_for('wordpress_installation'))
    return render_template('connect_server.html')


@app.route('/content_image_generation', methods=['GET', 'POST'])
@login_required
def content_image_generation():
    if request.method == 'POST':
        try:
            # Get the latest WordPress installation with its category and menu items
            wp_install = WordPressInstallation.query.filter_by(
                server_id=current_user.server_connections[-1].id if current_user.server_connections else None
            ).order_by(WordPressInstallation.id.desc()).first()

            if not wp_install or not wp_install.category_id:
                flash('Please select a website category first', 'warning')
                return redirect(url_for('website_category'))

            # Get category information
            category = WebsiteCategory.query.get(wp_install.category_id)
            if not category:
                logger.error(f"Category ID {wp_install.category_id} not found")
                flash('Error retrieving website category', 'danger')
                return render_template('content_image_generation.html')

            # Get menu items from session
            menu_items = session.get('generated_menu_items', [])

            # Import and initialize Gemini Content Trainer
            from gemini_content_trainer import GeminiContentTrainer
            trainer = GeminiContentTrainer()

            # Generate content prompt based on category and menu
            content_prompt = trainer.get_combined_prompt(category.name, menu_items)

            # Get image description prompt
            image_prompt = trainer.get_image_description_prompt(category.name, "Home")

            logger.info(f"Generated content prompt for {category.name} website")

            # Here you would call the Gemini API using the content_prompt
            # For now, we'll use a category-specific template
            if category.name in trainer.category_templates:
                template = trainer.category_templates[category.name]
                examples = template['content_examples']
                keywords = template['keywords']

                # Generate category-specific content using the template
                generated_content = f"""Welcome to our {category.name} website!

This professionally crafted content showcases our {keywords[0]} and {keywords[1]} in an engaging manner that highlights our {keywords[2]}. Our {category.name.lower()} is dedicated to providing exceptional {keywords[3]} and {keywords[4]} to all our customers.

{examples[0]}

Key features:
• Professional {keywords[0]} and implementation
• Customer-focused approach with emphasis on {keywords[1]}
• High-quality {keywords[2]} and {keywords[3]}
• Responsive {keywords[4]} support

{examples[1]}

Contact us today to learn more about how we can help you achieve your goals."""

                # Generate a category-specific image description
                generated_image_description = f"A professional image featuring our {category.name.lower()} branding against a clean background, with subtle design elements representing our industry and values. The imagery should showcase {template['focus']} with a {template['tone']} style. The color scheme matches our website palette with soft lighting that creates an inviting atmosphere."
            else:
                # Generic content for unknown categories
                generated_content = """Welcome to our website! 

This professionally crafted content showcases our products and services in an engaging manner. Our company is dedicated to providing exceptional quality and service to all our customers.

Key features:
• Professional design and implementation
• Customer-focused approach
• High-quality products and services
• Responsive customer support

Contact us today to learn more about how we can help you achieve your goals."""

                generated_image_description = "A professional image featuring our company logo against a clean background, with subtle design elements representing our industry and brand values. The color scheme matches our website palette with soft lighting that creates an inviting atmosphere."

            # Store the generated content in session
            session['content_generated'] = True
            session['generated_content'] = generated_content
            session['generated_image_description'] = generated_image_description
            session['content_generation_prompt'] = content_prompt  # Store for reference

            flash('Content has been successfully generated! You can now proceed to the next stage.', 'success')
            return render_template('content_image_generation.html')

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            flash(f'An error occurred during content generation: {str(e)}', 'danger')
            return render_template('content_image_generation.html')

    return render_template('content_image_generation.html')


@app.route('/content_preview', methods=['GET', 'POST'])
@login_required
def content_preview():
    generated_content = session.get('generated_content', '')
    generated_image_description = session.get('generated_image_description', '')

    # Get user's subscription plan
    subscription = SubscriptionPlan.query.filter_by(
        user_id=current_user.id, status='active').order_by(
            SubscriptionPlan.created_at.desc()).first()

    if subscription:
        session['subscription_plan'] = subscription.plan_type
    else:
        session['subscription_plan'] = 'free'

    # Get Stripe publishable key from environment
    stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    if not stripe_publishable_key:
        logger.warning("No STRIPE_PUBLISHABLE_KEY found. Using test key.")
        stripe_publishable_key = 'pk_test_sample'

    if request.method == 'POST' and request.files:
        try:
            # Handle image uploads
            uploaded_files = request.files.getlist('background_images')

            # Apply plan limits
            max_uploads = 1  # Free plan
            if session['subscription_plan'] == 'basic':
                max_uploads = 5
            elif session['subscription_plan'] == 'professional':
                max_uploads = 15
            elif session['subscription_plan'] == 'premium':
                max_uploads = 30

            if len(uploaded_files) > max_uploads:
                return jsonify({'success': False, 'error': f'Your plan only allows {max_uploads} uploads at once'})

            # Process uploads here
            # This is a placeholder for the image upload functionality
            return jsonify({'success': True, 'urls': ['https://example.com/image1.jpg']})

        except Exception as e:
            logger.error(f"Error uploading images: {e}")
            return jsonify({'success': False, 'error': str(e)})

    return render_template('content_preview.html', 
                          generated_content=generated_content,
                          generated_image_description=generated_image_description,
                          stripe_publishable_key=stripe_publishable_key)


@app.route('/generate_plan_content', methods=['POST'])
@login_required
def generate_plan_content():
    try:
        data = request.get_json()
        plan = data.get('plan', 'basic')

        # Verify active subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).order_by(SubscriptionPlan.created_at.desc()).first()

        if not subscription:
            return jsonify({
                'success': False, 
                'error': 'No active subscription found',
                'redirect': url_for('generate_content')
            }), 403

        # Check plan access level
        plan_levels = {
            'free': 0,
            'basic': 1,
            'professional': 2,
            'premium': 3
        }

        if plan_levels.get(plan, 0) > plan_levels.get(subscription.plan_type, 0):
            return jsonify({
                'success': False,
                'error': f'Your current subscription does not include {plan} plan features',
                'redirect': url_for('generate_content')
            }), 403

        # Verify Gemini API key is configured
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({
                'success': False,
                'error': 'Please configure your Gemini API key in the environment variables'
            }), 400

        # Ensure GEMINI_API_KEY is available
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return jsonify({
                'success': False, 
                'error': 'Gemini API key is not configured. Please contact support or try again later.'
            })

        # Quick validation of API key format
        if len(gemini_api_key) < 10:
            logger.warning("GEMINI_API_KEY appears invalid (too short)")
            return jsonify({
                'success': False, 
                'error': 'Gemini API configuration is invalid. Please contact support.'
            })

        # Configure Gemini API with the key if available
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            logger.info(f"Configured Gemini API for plan: {plan}")
        except ImportError:
            logger.error("Google Generative AI package not installed")
            return jsonify({
                'success': False,
                'error': 'The Gemini AI service is not properly configured. Please try again later.'
            })
        except Exception as config_error:
            logger.error(f"Error configuring Gemini API: {config_error}")
            return jsonify({
                'success': False,
                'error': 'Unable to connect to AI service. Please try again in a few minutes.'
            })

        # Verify user has appropriate subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id, status='active').order_by(
                SubscriptionPlan.created_at.desc()).first()

        if not subscription:
            return jsonify({'success': False, 'error': 'No active subscription found'})

        # Check if user's plan is sufficient
        if plan == 'professional' and subscription.plan_type not in ['professional', 'premium', 'enterprise']:
            return jsonify({'success': False, 'error': 'This feature requires Professional or higher plan'})

        if plan == 'premium' and subscription.plan_type not in ['premium', 'enterprise']:
            return jsonify({'success': False, 'error': 'This feature requires Premium or Enterprise plan'})

        if plan == 'enterprise' and subscription.plan_type != 'enterprise':
            return jsonify({'success': False, 'error': 'This feature requires Enterprise plan'})

        # Get the website category
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            return jsonify({'success': False, 'error': 'Website category not found'})

        category = WebsiteCategory.query.get(wp_install.category_id)

        # Get menu items
        menu_items = session.get('generated_menu_items', [])

        # Import Gemini Content Trainer and connect with Gemini API
        from gemini_content_trainer import GeminiContentTrainer
        from abilities import llm
        import google.generativeai as genai

        trainer = GeminiContentTrainer()

        # Generate additional content based on plan
        additional_content = {}

        # Setup generation config based on subscription plan
        generation_config = {
            "temperature": 0.7 if plan == 'basic' else 0.8,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024 if plan == 'basic' else 2048,
        }

        # Configure Gemini model based on plan
        model_name = "gemini-1.5-flash"  # Basic plan default
        if plan in ['professional', 'premium', 'enterprise']:
            # Use more advanced models for higher tier plans
            model_name = "gemini-1.5-pro"

        logger.info(f"Using Gemini model {model_name} for {plan} plan content generation")

        # Prepare content generation prompt based on plan and category
        if plan == 'basic':
            # Generate basic content with Gemini API
            blog_prompt = f"Generate a blog post for a {category.name} website about {trainer.category_templates.get(category.name, {}).get('keywords', ['the industry'])[0]}"
            about_prompt = f"Generate an About page for a {category.name} website focusing on company story and values"
            contact_prompt = f"Generate a Contact page for a {category.name} website with sample contact information"

            # Call Gemini API for content generation with configured model
            try:
                # Direct Gemini API calls with specific model
                model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)

                # Add timeout to generation config
                import concurrent.futures
                import time

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Set up async content generation tasks with timeout
                    blog_future = executor.submit(model.generate_content, blog_prompt)
                    about_future = executor.submit(model.generate_content, about_prompt)
                    contact_future = executor.submit(model.generate_content, contact_prompt)

                    # Get responses with timeout (10 seconds per request)
                    try:
                        blog_response = blog_future.result(timeout=10)
                        blog_text = blog_response.text if hasattr(blog_response, 'text') else generate_blog_post(trainer, category.name)
                    except (concurrent.futures.TimeoutError, Exception) as e:
                        logger.warning(f"Blog content generation timed out or failed: {str(e)}")
                        blog_text = generate_blog_post(trainer, category.name)

                    try:
                        about_response = about_future.result(timeout=10)
                        about_text = about_response.text if hasattr(about_response, 'text') else generate_about_page(trainer, category.name)
                    except (concurrent.futures.TimeoutError, Exception) as e:
                        logger.warning(f"About content generation timed out or failed: {str(e)}")
                        about_text = generate_about_page(trainer, category.name)

                    try:
                        contact_response = contact_future.result(timeout=10)
                        contact_text = contact_response.text if hasattr(contact_response, 'text') else generate_contact_page(trainer, category.name)
                    except (concurrent.futures.TimeoutError, Exception) as e:
                        logger.warning(f"Contact content generation timed out or failed: {str(e)}")
                        contact_text = generate_contact_page(trainer, category.name)

                additional_content['blog_post'] = blog_text
                additional_content['about_page'] = about_text
                additional_content['contact_page'] = contact_text

                logger.info(f"Successfully generated content with Gemini API for {plan} plan")

            except Exception as gemini_error:
                logger.error(f"Gemini API error: {gemini_error}")
                # Fallback to template-based generation
                additional_content['blog_post'] = generate_blog_post(trainer, category.name)
                additional_content['about_page'] = generate_about_page(trainer, category.name)
                additional_content['contact_page'] = generate_contact_page(trainer, category.name)

        elif plan in ['professional', 'premium', 'enterprise']:
            # Generate more advanced content with Gemini API
            combined_prompt = trainer.get_combined_prompt(category.name, menu_items)

            # Call Gemini API for professional+ content generation
            gemini_result = llm(message=combined_prompt, temperature=0.7)

            # Try to use Gemini API if available, otherwise use fallback
            gemini_result = {}
            try:
                # Use LLM helper if available
                from abilities import llm
                gemini_result = llm(message=combined_prompt, temperature=0.7)
                logger.info("Successfully called Gemini API")
            except Exception as llm_error:
                logger.error(f"Error calling Gemini API: {llm_error}")
                logger.info("Using fallback content generation")

            # Process the generated content or use fallback
            if gemini_result and 'response' in gemini_result:
                # Process the generated content into structured format
                generated_text = gemini_result.get('response', '')
                logger.info(f"Got {len(generated_text)} chars from Gemini API")

            # Always populate content structure to ensure something is returned
            # For professional plan
            additional_content['blog_posts'] = [generate_blog_post(trainer, category.name) for _ in range(5)]
            additional_content['all_pages'] = generate_all_pages(trainer, category.name, menu_items)
            additional_content['seo_content'] = generate_seo_content(trainer, category.name)
            additional_content['social_media'] = generate_social_media(trainer, category.name)

            # Add premium features for premium+ plans
            if plan in ['premium', 'enterprise']:
                additional_content['custom_templates'] = generate_custom_templates(trainer, category.name)
                additional_content['multi_language'] = generate_multi_language(trainer, category.name)
                additional_content['advanced_seo'] = generate_advanced_seo(trainer, category.name)

            # Add enterprise features
            if plan == 'enterprise':
                additional_content['landing_pages'] = [f"Landing page {i+1} for {category.name} website" for i in range(5)]
                additional_content['marketing_strategy'] = f"Comprehensive marketing strategy for {category.name} business"

        # Store the generated content in session
        if 'additional_generated_content' not in session:
            session['additional_generated_content'] = {}

        session['additional_generated_content'][plan] = additional_content

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error generating plan content: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})


# Helper functions for content generation based on plans
def generate_blog_post(trainer, category_name):
    # Generate a blog post for the given category
    return f"Sample blog post for {category_name} website. This would be a full blog post in a real implementation."


def generate_about_page(trainer, category_name):
    # Generate about page content
    return f"About page content for {category_name} website. This would describe the business or organization."


def generate_contact_page(trainer, category_name):
    # Generate contact page content
    return f"Contact page content for {category_name} website. This would include contact details and a form."


def generate_all_pages(trainer, category_name, menu_items):
    # Generate content for all pages based on menu items
    pages = {}
    for item in menu_items:
        if 'label' in item:
            pages[item['label']] = f"Content for {item['label']} page on {category_name} website."
    return pages


def generate_seo_content(trainer, category_name):
    # Generate SEO optimized content
    return {
        "meta_descriptions": f"SEO meta descriptions for {category_name} website.",
        "keywords": f"Relevant keywords for {category_name} website.",
        "headings": f"SEO optimized headings for {category_name} website."
    }


def generate_social_media(trainer, category_name):
    # Generate social media content
    return {
        "facebook": f"Facebook post templates for {category_name} website.",
        "twitter": f"Twitter post templates for {category_name} website.",
        "instagram": f"Instagram post templates for {category_name} website."
    }


def generate_custom_templates(trainer, category_name):
    # Generate custom content templates
    return {
        "product_template": f"Product description template for {category_name} website.",
        "service_template": f"Service description template for {category_name} website.",
        "event_template": f"Event description template for {category_name} website."
    }


def generate_multi_language(trainer, category_name):
    # Generate multi-language content
    return {
        "english": f"English content for {category_name} website.",
        "spanish": f"Spanish content for {category_name} website.",
        "french": f"French content for {category_name} website."
    }


def generate_advanced_seo(trainer, category_name):
    # Generate advanced SEO content
    return {
        "schema_markup": f"Schema markup for {category_name} website.",
        "canonical_tags": f"Canonical URL strategy for {category_name} website.",
        "internal_linking": f"Internal linking structure for {category_name} website."
    }


@app.route('/edit_plan/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def edit_plan(plan_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    return render_template('edit_plan.html', plan_id=plan_id)


@app.route('/documentation')
def documentation():
    return render_template('documentation_modal.html')


@app.route('/terms')
def terms():
    return render_template('terms_modal.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy_modal.html')


@app.route('/payment_policy')
def payment_policy():
    return render_template('payment_policy_modal.html')


@app.route('/faq')
def faq():
    return render_template('faq_modal.html')


@app.route('/gemini_admin', methods=['GET', 'POST'])
@login_required
def gemini_admin():
    # Only allow admins to access this page
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('home'))

    # Get all website categories
    categories = WebsiteCategory.query.order_by(WebsiteCategory.name).all()

    training_data = None

    if request.method == 'POST':
        try:
            # Get form data
            category_id = request.form.get('category')
            menu_items = request.form.getlist('menu_items')
            custom_menu_item = request.form.get('custom_menu_item')
            model = request.form.get('model')
            temperature = float(request.form.get('temperature', 0.7))

            # Get category
            category = WebsiteCategory.query.get(category_id)
            if not category:
                flash('Invalid category selected', 'danger')
                return render_template('gemini_content_admin.html', categories=categories)

            # Process menu items
            processed_menu_items = []
            for item in menu_items:
                if item == 'Custom' and custom_menu_item:
                    menu_dict = {'label': custom_menu_item, 'description': f'Custom {custom_menu_item} page', 'slug': custom_menu_item.lower().replace(' ', '-')}
                else:
                    menu_dict = {'label': item, 'description': f'{item} page for {category.name} website', 'slug': item.lower()}
                processed_menu_items.append(menu_dict)

            # Import and initialize Gemini Content Trainer
            from gemini_content_trainer import GeminiContentTrainer
            trainer = GeminiContentTrainer()

            # Generate training prompts
            category_prompt = trainer.get_category_prompt(category.name)

            # Generate menu-specific prompts
            menu_prompts = {}
            for item in processed_menu_items:
                menu_prompts[item['label']] = trainer.get_menu_prompt(item['label'])

            # Generate combined prompt
            combined_prompt = trainer.get_combined_prompt(category.name, processed_menu_items)

            # Generate image prompt
            image_prompt = trainer.get_image_description_prompt(category.name, "Home")

            # Prepare training data for template
            training_data = {
                'category_prompt': category_prompt,
                'menu_prompts': menu_prompts,
                'combined_prompt': combined_prompt,
                'image_prompt': image_prompt,
                'category': category.name,
                'model': model,
                'temperature': temperature
            }

            flash('Training prompts generated successfully', 'success')

        except Exception as e:
            logger.error(f"Error generating training prompts: {e}")
            logger.error(traceback.format_exc())
            flash(f'Error generating training prompts: {str(e)}', 'danger')

    return render_template('gemini_content_admin.html', categories=categories, training_data=training_data)


@app.route('/payment/cancel')
def payment_cancel():
    flash('Payment cancelled')
    return redirect(url_for('generate_content'))


@app.route('/payment/success')
def payment_success():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            flash('Invalid payment session', 'error')
            return redirect(url_for('generate_content'))

        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Create subscription record
        subscription = SubscriptionPlan(
            user_id=current_user.id,
            stripe_customer_id=session.customer,
            stripe_subscription_id=session.subscription,
            plan_type=session.metadata.get('plan_type', 'basic'),
            status='active',
            created_at=datetime.utcnow()
        )
        db.session.add(subscription)
        db.session.commit()

        # Store subscription in session
        session['subscription_plan'] = subscription.plan_type

        flash('Payment successful! You can now generate content based on your subscription.', 'success')
        return redirect(url_for('content_image_generation'))
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        flash('Error processing payment confirmation. Please contact support.', 'error')
        return redirect(url_for('generate_content'))


@app.route('/website_builder_intro')
def website_builder_intro():
    return render_template('website_builder_intro.html')


@app.route('/content_generation_intro')
def content_generation_intro():
    return render_template('content_generation_intro.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/chat/send', methods=['POST'])
@login_required
def chat_send():
    message = request.json.get('message')
    # Use LLM to generate AI response
    try:
        # Special command to list models
        if message.lower().strip() == "list models":
            from abilities import list_available_models
            models_info = list_available_models()
            if "error" in models_info:
                return jsonify({
                    'response':
                    f"Error listing models: {models_info['error']}"
                })

            available_models = models_info.get("available_models", [])
            if available_models:
                models_text = "\n".join([f"- {model}" for model in available_models])
                return jsonify({'response': f"Available Gemini models:\n{models_text}"})
            else:
                return jsonify({
                    'response':
                    "No available modelsfound. Please check your Google Cloud API permissions."
                })

        response_schema = {
            'type': 'object',
            'properties': {
                'response': {
                    'type': 'string'
                }
            },
            'required': ['response']
        }

        message_prompt = f"""You are an AI assistant for a WordPress Automation Tool. 
            Provide a helpful, concise, and engaging response to the following user message:

            User message: {message}

            Respond in a friendly, professional tone that reflects the tool's purpose of helping users create and manage WordPress websites. 
            If the user asks about website topics, provide relevant information about WordPress features, plugins, or themes.
            For documentation, tutorials, or case studies, be sure to provide proper page links in markdown format like [page name](/route_name).
            Relevant routes you can link to include: [/documentation](/documentation), [/tutorials](/tutorials), [/case_studies](/case_studies), 
            [/generate_content](/generate_content), [/optimization](/optimization)."""

        ai_response = llm(message=message_prompt, temperature=0.7)

        response_text = ai_response.get(
            'response', 'I apologize, but I could not generate a response.')

        # Log successful AI response generation
        logger.info(f"AI response generated: {response_text}")

        # Save the chat message to database
        try:
            chat_message = ChatMessage(user_id=current_user.id,
                                       message=message,
                                       response=response_text)
            db.session.add(chat_message)
            db.session.commit()
            logger.info(f"Chat message saved for user {current_user.id}")
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            db.session.rollback()
            # Continue with response even if saving fails

        return jsonify({'response': response_text})
    except Exception as e:
        logger.error(f"Chat AI error: {e}")
        return jsonify({
            'response':
            'Sorry, there was an error processing your request. Our team has been notified.'
        })


@app.route('/chat_history')
@login_required
def chat_history():
    try:
        # Get chat history for the current user
        messages = ChatMessage.query.filter_by(
            user_id=current_user.id).order_by(
                ChatMessage.created_at.desc()).all()
        return render_template('chat_history.html', messages=messages)
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        flash('There was an error loading your chat history.', 'error')
        return redirect(url_for('user_dashboard'))


@app.route('/optimization', methods=['GET', 'POST'])
@login_required
def optimization():
    if request.method == 'POST':
        try:
            # Get the latest WordPress installation
            wp_install = WordPressInstallation.query.filter_by(
                server_id=current_user.server_connections[-1].id if current_user.server_connections else None
            ).order_by(WordPressInstallation.id.desc()).first()

            if not wp_install:
                flash('No WordPress installation found', 'warning')
                return render_template('optimization.html')

            # Process Google Analytics settings
            ga_tracking_id = request.form.get('ga_tracking_id')
            ga_enhanced_ecommerce = 'ga_enhanced_ecommerce' in request.form
            ga_demographics = 'ga_demographics' in request.form

            # Process Google Ads settings
            ads_conversion_id = request.form.get('ads_conversion_id')
            ads_remarketing_tag = request.form.get('ads_remarketing_tag')
            ads_dynamic_remarketing = 'ads_dynamic_remarketing' in request.form

            # Process Performance settings
            enable_page_caching = 'enable_page_caching' in request.form
            enable_browser_caching = 'enable_browser_caching' in request.form
            enable_object_caching = 'enable_object_caching' in request.form
            enable_image_optimization = 'enable_image_optimization' in request.form
            enable_lazy_loading = 'enable_lazy_loading' in request.form
            enable_minification = 'enable_minification' in request.form
            cdn_provider = request.form.get('cdn_provider')
            cdn_url = request.form.get('cdn_url')

            # Check for required fields if user is trying to configure specific services
            form_warnings = []

            # Validate Google Analytics tracking ID if provided
            if ga_tracking_id and not (ga_tracking_id.startswith('UA-') or ga_tracking_id.startswith('G-')):
                form_warnings.append('Invalid Google Analytics tracking ID format. Should start with UA- or G-.')

            # Validate Google Ads ID if provided
            if ads_conversion_id and not ads_conversion_id.startswith('AW-'):
                form_warnings.append('Invalid Google Ads conversion ID format. Should start with AW-.')

            # Check if any of the required fields are filled when trying to use specific features
            if (not ga_tracking_id) and (ga_enhanced_ecommerce or ga_demographics):
                form_warnings.append('Google Analytics tracking ID is required to enable enhanced features.')

            # Validate CDN URL if CDN provider is selected
            if cdn_provider and not cdn_url:
                form_warnings.append('CDN URL is required when a CDN provider is selected.')

            # If there are warnings, show them and stay on the page
            if form_warnings:
                for warning in form_warnings:
                    flash(warning, 'warning')
                return render_template('optimization.html')

            # Store optimization settings in session
            session['optimization_settings'] = {
                'ga_tracking_id': ga_tracking_id,
                'ga_enhanced_ecommerce': ga_enhanced_ecommerce,
                'ga_demographics': ga_demographics,
                'ads_conversion_id': ads_conversion_id,
                'ads_remarketing_tag': ads_remarketing_tag,
                'ads_dynamic_remarketing': ads_dynamic_remarketing,
                'enable_page_caching': enable_page_caching,
                'enable_browser_caching': enable_browser_caching,
                'enable_object_caching': enable_object_caching,
                'enable_image_optimization': enable_image_optimization,
                'enable_lazy_loading': enable_lazy_loading,
                'enable_minification': enable_minification,
                'cdn_provider': cdn_provider,
                'cdn_url': cdn_url
            }

            # In a real implementation, you would apply these settings to the WordPress site
            # using the WordPress REST API or other integration methods

            # Initialize WordPress API client
            wp_api = WordPressRestAPI(
                base_url=f"https://{wp_install.site_url}",
                username=wp_install.admin_username,
                password=wp_install.admin_password)

            # Apply optimization settings to WordPress site
            # This is a placeholder for the actual implementation
            optimization_applied = True

            if optimization_applied:
                flash('Optimization settings applied successfully!', 'success')
            else:
                flash('Error applying optimization settings. Please try again.', 'danger')

            return redirect(url_for('summary'))

        except Exception as e:
            logger.error(f"Error applying optimization settings: {e}")
            logger.error(traceback.format_exc())
            flash(f'An error occurred: {str(e)}', 'danger')

    # For GET requests, display the form with any existing settings
    optimization_settings = session.get('optimization_settings', {})
    return render_template('optimization.html', settings=optimization_settings)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Check if it's a social signup
            if 'social_token' in request.form:
                # Process social signup
                social_token = request.form['social_token']
                social_provider = request.form['social_provider']
                email = request.form['email']

                # Validate social token (in a real app you'd verify this with the provider)
                if not social_token or not social_provider or not email:
                    flash('Invalid social authentication data', 'error')
                    return render_template('signup.html')

                # Check if user already exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    # Log the user in
                    login_user(existing_user)
                    existing_user.record_login()
                    db.session.commit()
                    return redirect(url_for('user_dashboard'))

                # Create new user with social auth
                user = User(email=email)
                # Generate a random secure password for social users
                random_password = str(uuid.uuid4())
                user.set_password(random_password)
                db.session.add(user)
                db.session.commit()

                # Log the user in
                login_user(user)
                user.record_login()
                db.session.commit()
                logger.info(
                    f"New social user created: {email} via {social_provider}")
                return redirect(url_for('user_dashboard'))

            # Regular email signup
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if not email or not password or not confirm_password:
                flash('Email, password and password confirmation are required',
                      'error')
                return render_template('signup.html')

            if len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
                return render_template('signup.html')

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('signup.html')

            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(
                    'Email already registered. Please login or use a different email.',
                    'error')
                return render_template('signup.html')

            # Create the user
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Auto-login the user after signup
            login_user(user)
            user.record_login()
            db.session.commit()

            logger.info(f"New user created: {email}")
            flash('Account created successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating account: {str(e)}")
            logger.error(traceback.format_exc())
            flash('Error creating account. Please try again.', 'error')
            return render_template('signup.html')
    return render_template('signup.html')


@app.route('/google_login')
def google_login():
    """Handle Google OAuth login"""
    try:
        # In a real implementation, you would:
        # 1. Redirect to Google OAuth URL
        # 2. Get authorization code
        # 3. Exchange for token
        # 4. Get user info from Google API

        # For demo purposes, we'll simulate a successful OAuth flow
        # In production, use a library like authlib or oauthlib

        # Normally this would come from Google's API
        simulated_user_info = {
            'email': request.args.get('email', 'google_user@example.com'),
            'token': 'simulated_token_' + str(uuid.uuid4()),
            'provider': 'google'
        }

        # Check if user exists
        user = User.query.filter_by(email=simulated_user_info['email']).first()

        if user:
            # User exists, log them in
            login_user(user)
            user.record_login()
            db.session.commit()
            logger.info(f"Google user logged in: {user.email}")
            return redirect(url_for('user_dashboard'))
        else:
            # New user, register them first
            user = User(email=simulated_user_info['email'])
            # Generate a random secure password for social users
            random_password = str(uuid.uuid4())
            user.set_password(random_password)
            db.session.add(user)
            db.session.commit()

            # Log the new user in
            login_user(user)
            user.record_login()
            db.session.commit()
            logger.info(
                f"New Google user registered and logged in: {user.email}")
            return redirect(url_for('user_dashboard'))

    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        flash('Error during Google authentication. Please try again.', 'error')
        return redirect(url_for('login'))


@app.route('/facebook_login')
def facebook_login():
    """Handle Facebook OAuth login"""
    try:
        # In a real implementation, you would:
        # 1. Redirect to Facebook OAuth URL
        # 2. Get authorization code
        # 3. Exchange for token
        # 4. Get user info from Facebook API

        # For demo purposes, we'll simulate a successful OAuth flow
        # In production, use a library like authlib or oauthlib

        # Normally this would come from Facebook's API
        simulated_user_info = {
            'email': request.args.get('email', 'facebook_user@example.com'),
            'token': 'simulated_token_' + str(uuid.uuid4()),
            'provider': 'facebook'
        }

        # Check if user exists
        user = User.query.filter_by(email=simulated_user_info['email']).first()

        if user:
            # User exists, log them in
            login_user(user)
            user.record_login()
            db.session.commit()
            logger.info(f"Facebook user logged in: {user.email}")
            return redirect(url_for('user_dashboard'))
        else:
            # New user, register them first
            user = User(email=simulated_user_info['email'])
            # Generate a random secure password for social users
            random_password = str(uuid.uuid4())
            user.set_password(random_password)
            db.session.add(user)
            db.session.commit()

            # Log the new user in
            login_user(user)
            user.record_login()
            db.session.commit()
            logger.info(
                f"New Facebook user registered and logged in: {user.email}")
            return redirect(url_for('user_dashboard'))

    except Exception as e:
        logger.error(f"Facebook login error: {str(e)}")
        flash('Error during Facebook authentication. Please try again.',
              'error')
        return redirect(url_for('login'))


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    try:
        # Verify the user is authenticated (extra check)
        if not current_user.is_authenticated:
            logger.warning("User not authenticated in user_dashboard route")
            return redirect(url_for('login'))

        # Get user data
        user_data = {
            'email': current_user.email,
            'last_login': current_user.last_login,
            'created_at': current_user.created_at
        }

        # Get chat history for user dashboard - handle case where there are no messages yet
        try:
            chat_messages = ChatMessage.query.filter_by(
                user_id=current_user.id).order_by(
                    ChatMessage.created_at.desc()).limit(5).all()
        except Exception as chat_err:
            logger.warning(f"Could not load chat messages: {chat_err}")
            chat_messages = []

        # Check if this is the first login after registration
        first_login = session.pop('first_login', False)
        if first_login:
            flash(
                'Welcome to your dashboard! Your account has been created successfully.',
                'success')

        logger.info(f"Rendering dashboard for user {current_user.id}")
        return render_template('user_dashboard.html',
                               user=user_data,
                               chat_messages=chat_messages)
    except Exception as e:
        logger.error(f"Error accessing dashboard: {e}")
        logger.error(traceback.format_exc())
        flash('Error loading dashboard', 'error')
        return redirect(url_for('home'))


@app.route('/api/check_updates/<int:installation_id>/<update_type>')
@login_required
def check_updates(installation_id, update_type):
    # Check for WordPress updates
    return jsonify({'updates_available': []})


@app.route('/summary')
@login_required
def summary():
    # Get the latest WordPress installation
    wp_install = WordPressInstallation.query.filter_by(
        server_id=current_user.server_connections[-1].id if current_user.server_connections else None
    ).order_by(WordPressInstallation.id.desc()).first()

    # Get category and theme
    category = None
    theme = None

    if wp_install:
        if wp_install.category_id:
            category = WebsiteCategory.query.get(wp_install.category_id)
        if wp_install.theme_id:
            theme = Theme.query.get(wp_install.theme_id)

    # Get optimization settings
    optimization_settings = session.get('optimization_settings', {})

    return render_template('summary.html', 
                          wp_install=wp_install,
                          category=category,
                          theme=theme,
                          optimization_settings=optimization_settings)


@app.route('/api/wordpress_details')
@login_required
def get_wordpress_details():
    """Get details of the user's WordPress installation"""
    try:
        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        # Get category and theme info if available
        category = None
        theme = None

        if wp_install:
            if wp_install.category_id:
                category = WebsiteCategory.query.get(wp_install.category_id)
            if wp_install.theme_id:
                theme = Theme.query.get(wp_install.theme_id)

        # Format the response
        response = {
            'installation': wp_install.to_dict() if wp_install else None,
            'category': category.to_dict() if category else None,
            'theme': theme.to_dict() if theme else None
        }

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting WordPress details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_current_stage')
@login_required
def get_current_stage():
    """Get the current installation stage to resume from"""
    try:
        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        # Determine current stage based on the installation state
        if not wp_install:
            return jsonify({'stage': 1, 'redirect_url': '/connect_server'})

        if not wp_install.category_id:
            return jsonify({'stage': 3, 'redirect_url': '/website_category'})

        if not wp_install.theme_id:
            return jsonify({'stage': 4, 'redirect_url': '/select_theme'})

        # Check if menu is generated
        if not session.get('generated_menu_items'):
            return jsonify({'stage': 5, 'redirect_url': '/generate_menu'})

        # Check if subscription exists
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id, status='active').first()

        if not subscription:
            return jsonify({'stage': 6, 'redirect_url': '/generate_content'})

        # Check if content is generated
        if not session.get('content_generated'):
            return jsonify({'stage': 7, 'redirect_url': '/content_image_generation'})

        # Default to content preview
        return jsonify({'stage': 8, 'redirect_url': '/content_preview'})

    except Exception as e:
        logger.error(f"Error determining current stage: {e}")
        return jsonify({'error': str(e), 'redirect_url': '/connect_server'}), 500

@app.route('/api/get_generated_content', methods=['GET'])
@login_required
def get_generated_content():
    """Get generated content for a specific plan"""
    try:
        plan = request.args.get('plan')

        # Get content from session
        additional_content = {}

        if 'additional_generated_content' in session and plan in session['additional_generated_content']:
            additional_content = session['additional_generated_content'][plan]
            return jsonify({'success': True, 'content': additional_content})

        # If no content found in session, check if we need to generate placeholder content
        # based on the user's subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id, status='active').order_by(
                SubscriptionPlan.created_at.desc()).first()

        if not subscription:
            return jsonify({'success': False, 'error': 'No active subscription found'}), 400

        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            return jsonify({'success': False, 'error': 'Website category not found'}), 400

        category = WebsiteCategory.query.get(wp_install.category_id)

        # Fallback to empty structure
        if plan == 'basic':
            additional_content = {
                'blog_post': '',
                'about_page': '',
                'contact_page': ''
            }
        elif plan == 'professional':
            additional_content = {
                'blog_posts': [],
                'all_pages': {},
                'seo_content': {},
                'social_media': {}
            }
        elif plan == 'premium':
            additional_content = {
                'blog_posts': [],
                'custom_templates': {},
                'multi_language': {},
                'advanced_seo': {}
            }

        return jsonify({'success': False, 'error': 'No content generated yet'}), 404

    except Exception as e:
        logger.error(f"Error fetching generated content: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

    # Get category and theme
    category = None
    theme = None


@app.route('/api/upload_wordpress_media', methods=['POST'])
@login_required
def upload_wordpress_media():
    """Upload images to WordPress Media Library via REST API"""
    try:
        # Check for image files in the request
        if 'images' not in request.files:
            return jsonify({'error': 'No images found in request'}), 400

        images = request.files.getlist('images')
        if not images or len(images) == 0:
            return jsonify({'error': 'No images found in request'}), 400

        # Get alt text (optional)
        alt_text = request.form.get('alt_text', '')

        # Get user's subscription plan to enforce limits
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id, status='active').order_by(
                SubscriptionPlan.created_at.desc()).first()

        plan_type = 'free'
        if subscription:
            plan_type = subscription.plan_type

        # Set max uploads based on plan
        max_uploads = 1  # Default for free plan
        if plan_type == 'basic':
            max_uploads = 5
        elif plan_type == 'professional':
            max_uploads = 15
        elif plan_type == 'premium':
            max_uploads = 30

        if len(images) > max_uploads:
            return jsonify({
                'error': f'Your {plan_type} plan allows a maximum of {max_uploads} image uploads'
            }), 400

        # Get the WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        if not wp_install:
            return jsonify({'error': 'No WordPress installation found'}), 404

        # Initialize WordPress API client
        wp_api = WordPressRestAPI(
            base_url=f"https://{wp_install.site_url}",
            username=wp_install.admin_username,
            password=wp_install.admin_password
        )

        # Upload each image
        uploaded_images = []
        for image in images:
            # Validate file type
            if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                continue

            # Upload to WordPress
            image_data = wp_api.upload_media(image, alt_text)
            if image_data:
                uploaded_images.append({
                    'id': image_data.get('id'),
                    'url': image_data.get('source_url'),
                    'filename': image_data.get('slug'),
                    'alt': alt_text
                })

        return jsonify({
            'success': True,
            'uploaded_count': len(uploaded_images),
            'images': uploaded_images
        })

    except Exception as e:
        logger.error(f"Error uploading media to WordPress: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to upload images: {str(e)}'}), 500


@app.route('/api/sync_wordpress_content', methods=['POST'])
@login_required
def sync_wordpress_content():
    """Sync generated content to WordPress"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No content data provided'}), 400

        content_type = data.get('content_type', 'post')  # post, page, etc.
        content_data = data.get('content_data', {})
        plan = data.get('plan', 'basic')

        if not content_data:
            return jsonify({'error': 'No content data provided'}), 400

        # Verify the user has an active subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id, status='active').order_by(
                SubscriptionPlan.created_at.desc()).first()

        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 403

        # Get the WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id if current_user.server_connections else None
        ).order_by(WordPressInstallation.id.desc()).first()

        if not wp_install:
            return jsonify({'error': 'No WordPress installation found'}), 404

        # Initialize WordPress API client
        wp_api = WordPressRestAPI(
            base_url=f"https://{wp_install.site_url}",
            username=wp_install.admin_username,
            password=wp_install.admin_password
        )

        # Sync content to WordPress
        result = wp_api.sync_generated_content(content_data, content_type)

        if not result:
            return jsonify({'success': False, 'error': 'Failed to sync content to WordPress'}), 500

        return jsonify({
            'success': True,
            'content_id': result.get('id'),
            'content_url': result.get('link'),
            'content_status': result.get('status'),
            'message': f"Successfully synced {content_type} to WordPress"
        })

    except Exception as e:
        logger.error(f"Error syncing content to WordPress: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

        try:
            uploaded_images.append({
                'id': image_data.get('id'),
                'url': image_data.get('source_url'),
                'filename': image_data.get('slug'),
                'alt': alt_text
            })

            return jsonify({
                'success': True,
                'uploaded_count': len(uploaded_images),
                'images': uploaded_images
            })

        except Exception as e:
            logger.error(f"Error uploading media to WordPress: {e}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Failed to upload images: {str(e)}'}), 500

        if wp_install:
            if wp_install.category_id:
                category = WebsiteCategory.query.get(wp_install.category_id)
            if wp_install.theme_id:
                theme = Theme.query.get(wp_install.theme_id)

        # Get optimization settings
        optimization_settings = session.get('optimization_settings', {})

        return render_template('summary.html', 
                    wp_install=wp_install,
                    category=category,
                    theme=theme,
                    optimization_settings=optimization_settings)

@app.route('/terms_agreement')
def terms_agreement():
    return render_template('saas_terms.html')


from wordpress_rest_api import WordPressRestAPI
from app_init import app
from abilities import url_for_uploaded_file

from app_init import app
from flask_login import login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger(__name__)


@app.route("/timeline_stages")
def timeline_stages():
    """Render the timeline stages page showing automation workflow"""
    try:
        return render_template('timeline_stages.html')
    except Exception as e:
        logger.error(f"Error rendering timeline stages: {e}")
        flash('Error loading timeline')
        return redirect(url_for('home'))


from abilities import upload_file_to_storage
from abilities import llm
from app_init import app
from flask_login import login_required
import logging


@app.route("/")
def home():
    return render_template('home.html')


# Rate limiting setup
limiter = Limiter(app=app,
                  key_func=get_remote_address,
                  storage_uri="memory://",
                  default_limits=["200 per day", "50 per hour"])


@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("60 per minute")
def login():
    logger.info("Processing login request")

    is_admin_login = request.args.get('admin', 'false') == 'true'

    if current_user.is_authenticated:
        logger.info(f"User {current_user.id} already authenticated")
        return redirect(
            url_for('admin_dashboard' if current_user.
                    is_admin else 'user_dashboard'))

    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                logger.warning("Login attempt with missing credentials")
                flash('Please provide both email and password')
                return render_template('login.html',
                                       is_admin_login=is_admin_login)

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                if is_admin_login and not user.is_admin:
                    flash('Access denied. Admin privileges required.')
                    return render_template('login.html', is_admin_login=True)

                login_user(user, remember=True)
                user.record_login()
                db.session.commit()
                logger.info(f"User {user.id} logged in successfully")
                session.pop('_flashes', None)

                next_page = request.args.get('next')
                return redirect(next_page or url_for(
                    'admin_dashboard' if is_admin_login else 'user_dashboard'))

            # Invalid login attempt
            if user:
                logger.warning(f"Failed login attempt for user {email}")
                user.record_failed_attempt()
            flash('Invalid email or password')
            return render_template('login.html', is_admin_login=is_admin_login)

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            logger.error(traceback.format_exc())
            flash('An error occurred during login. Please try again.')

    return render_template('login.html', is_admin_login=is_admin_login)


@app.route("/website_category", methods=['GET', 'POST'])
def website_category():

    try:
        # First, ensure all categories exist in the database
        default_categories = [{
            'name':
            'eCommerce',
'description':
            'Build an online store to sell products or services with features like shopping cart, payment processing, and inventory management'
        }, {
            'name':
            'Restaurant',
            'description':
            'Create a restaurant website with menu displays, online ordering, reservations, and location information'
        }, {
            'name':
            'Blog',
            'description':
            'Start a blog with a clean layout focused on content, categories, comments, and social sharing'
        }, {
            'name':
            'Portfolio',
            'description':
            'Showcase your work with a professional portfolio featuring galleries, project descriptions, and contact information'
        }, {
            'name':
            'Business',
            'description':
            'Present your business with a professional website including services, about us, testimonials, and contact forms'
        }, {
            'name':
            'News',
            'description':
            'Create a news website with article categories, featured stories, and multimedia content'
        }, {
            'name':
            'Social Network',
            'description':
            'Build a community website with user profiles, activity feeds, and member interactions'
        }, {
            'name':
            'Educational',
            'description':
            'Develop an educational website with course listings, learning resources, and student portals'
        }, {
            'name':
            'Real Estate',
            'description':
            'List properties with detailed information, photo galleries, and property search functionality'
        }, {
            'name':
            'Nonprofit',
            'description':
            'Create a nonprofit website with donation systems, event calendars, and volunteer signups'
        }]

        # Ensure all default categories exist in the database
        for cat_data in default_categories:
            category = WebsiteCategory.query.filter_by(
                name=cat_data['name']).first()
            if not category:
                new_category = WebsiteCategory(
                    name=cat_data['name'], description=cat_data['description'])
                db.session.add(new_category)
                logger.info(f"Added missing category: {cat_data['name']}")

        db.session.commit()

        # Now fetch all categories ordered by ID
        categories = WebsiteCategory.query.order_by(WebsiteCategory.id).all()
        logger.info(f"Retrieved {len(categories)} website categories")

        if request.method == 'POST':
            if not current_user.server_connections:
                flash(
                    'No server connection found. Please connect your server first.'
                )
                return redirect(url_for('connect_server'))

            category_id = request.form.get('category')
            if not category_id:
                flash('Please select a category')
                return redirect(url_for('website_category'))

            wp_install = WordPressInstallation.query.filter_by(
                server_id=current_user.server_connections[-1].id).order_by(
                    WordPressInstallation.id.desc()).first()

            if wp_install:
                wp_install.category_id = category_id
                db.session.commit()
                return redirect(url_for('select_theme'))
            else:
                flash('No WordPress installation found')
                return redirect(url_for('wordpress_installation'))

        return render_template('website_category.html',
                               categories=categories,
                               current_stage=3,
                               total_stages=8)

    except Exception as e:
        logger.error(f"Error in website category selection: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('wordpress_installation'))


@app.route("/select_theme", methods=['GET', 'POST'])
@login_required
def select_theme():
    try:
        # Get the latest WordPress installation's category
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id).order_by(
                WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            flash('Please select a website category first')
            return redirect(url_for('website_category'))

        # Get category information
        category = WebsiteCategory.query.get(wp_install.category_id)

        # Get themes for this category
        themes = Theme.query.filter_by(
            category_id=wp_install.category_id).all()

        # If no themes found, create sample themes for this category
        if not themes:
            logger.warning(
                f"No themes found for category {category.name}. Creating default themes."
            )
            try:
                # Create sample themes for this category
                default_themes = [{
                    'name': f'{category.name} Modern',
                    'description':
                    f'A modern, minimalist theme for {category.name} websites with clean design and intuitive navigation',
                    'thumbnail_url': 'https://example.com/modern-thumb.jpg',
                    'demo_url': 'https://example.com/modern-demo'
                }, {
                    'name':
                    f'{category.name} Classic',
                    'description':
                    f'A classic design for {category.name} websites with traditional layout and strong typography',
                    'thumbnail_url':
                    'https://example.com/classic-thumb.jpg',
                    'demo_url':
                    'https://example.com/classic-demo'
                }, {
                    'name':
                    f'{category.name} Premium',
                    'description':
                    f'A premium theme for {category.name} websites with advanced features and customization options',
                    'thumbnail_url':
                    'https://example.com/premium-thumb.jpg',
                    'demo_url':
                    'https://example.com/premium-demo'
                }]

                for theme_data in default_themes:
                    theme = Theme(name=theme_data['name'],
                                  description=theme_data['description'],
                                  thumbnail_url=theme_data['thumbnail_url'],
                                  demo_url=theme_data['demo_url'],
                                  category_id=category.id)
                    db.session.add(theme)

                db.session.commit()
                themes = Theme.query.filter_by(
                    category_id=wp_install.category_id).all()
                logger.info(
                    f"Created {len(themes)} themes for category {category.name}"
                )
            except Exception as theme_error:
                logger.error(f"Error creating themes: {theme_error}")
                logger.error(f"Traceback: {traceback.format_exc()}")

        if request.method == 'POST':
            theme_id = request.form.get('theme')

            if wp_install:
                wp_install.theme_id = theme_id
                db.session.commit()
                logger.info(
                    f"Theme {theme_id} selected for installation {wp_install.id}"
                )
                return redirect(url_for('generate_menu'))

        # Debug info
        logger.info(
            f"Rendering theme_selection.html with {len(themes)} themes for category {category.name}"
        )
        for theme in themes:
            logger.info(f"Theme: {theme.id} - {theme.name}")

        return render_template('theme_selection.html',
                               themes=themes,
                               category=category,
                               current_stage=4,
                               total_stages=8)

    except Exception as e:
        logger.error(f"Error in theme selection: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('website_category'))


@app.route("/generate_menu", methods=['GET', 'POST'])
@login_required
def generate_menu():
    try:
        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id).order_by(
                WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            flash('Please select a website category first')
            return redirect(url_for('website_category'))

        # Get the category name
        category = WebsiteCategory.query.get(wp_install.category_id)

        if request.method == 'POST':
            # Use LLM to generate menu items based on category
            menu_generation_prompt = f"""
            Generate a professional WordPress menu structure for a {category.name} website. 
            Provide 4-6 main menu items that are most relevant and user-friendly. 
            Each menu item should have a clear, concise label and a brief description of its purpose.
            """

            menu_schema = {
                'type': 'object',
                'properties': {
                    'menu_items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'label': {
                                    'type': 'string'
                                },
                                'slug': {
                                    'type': 'string'
                                },
                                'description': {
                                    'type': 'string'
                                }
                            },
                            'required': ['label', 'slug', 'description']
                        }
                    }
                },
                'required': ['menu_items']
            }

            # Use LLM to generate menu
            menu_result = llm(message=menu_generation_prompt,
                              response_schema=menu_schema,
                              model='gpt-4o-mini',
                              temperature=0.7,
                              image_url=None)

            # Initialize WordPress API client
            wp_api = WordPressRestAPI(
                base_url=f"https://{wp_install.site_url}",
                username=wp_install.admin_username,
                password=wp_install.admin_password)

            # Create menu in WordPress
            menu_items = menu_result.get('menu_items', [])
            if wp_api.create_menu(menu_items):
                # Store menu items in session
                session['generated_menu_items'] = menu_items
                flash('Menu generated and published successfully!')
            else:
                flash('Menu generated but could not be published to WordPress')

            return redirect(url_for('generate_content'))

        # GET request - show form
        menu_items = session.get('generated_menu_items', [])
        return render_template('generate_menu.html',
                               category=category,
                               current_stage=5,
                               total_stages=8,
                               menu_items=menu_items)

    except Exception as e:
        logger.error(f"Error generating menu: {e}")
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('website_category'))


@app.route("/generate_content", methods=['GET', 'POST'])
@login_required
def generate_content():
    try:
        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id).order_by(
                WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            flash('Please select a website category first')
            return redirect(url_for('website_category'))

        # Get the category name
        category = WebsiteCategory.query.get(wp_install.category_id)

        if request.method == 'POST':
            plan = request.form.get('plan')
            if plan == 'free':
                subscription = SubscriptionPlan(user_id=current_user.id,
                                                plan_type='free',
                                                status='active',
                                                created_at=datetime.utcnow())
                db.session.add(subscription)
                db.session.commit()
                flash('Free plan activated successfully!')
                return redirect(url_for('content_image_generation'))

        # Get Stripe publishable key from environment
        stripe_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        if not stripe_key:
            logger.warning("No STRIPE_PUBLISHABLE_KEY found. Using test key.")
            stripe_key = 'pk_test_sample'

        return render_template('generate_content.html',
                               category=category,
                               current_stage=6,
                               total_stages=8,
                               stripe_publishable_key=stripe_key)

    except Exception as e:
        logger.error(f"Error in content generation: {e}")
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('generate_menu'))


from app_init import app
import logging
import stripe
from flask_login import login_required

# Configure Stripe with test key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe.api_version = '2024-04-10'  # Updated to latest Stripe API version
logger.info(f"Stripe API Key Loaded: {bool(stripe.api_key)}")  # Log key presence for debugging

# Ensure Stripe.js is properly loaded in the template
stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_sample')


@app.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    """
    Creates a Stripe checkout session for subscription
    :return: JSON response with checkout URL or error
    """
    try:
        plan_type = request.form.get('plan')
        display_currency = request.form.get('display_currency', 'USD')

        logger.info(f"Creating checkout session for plan: {plan_type}, currency: {display_currency}")

        if not plan_type:
            return jsonify({'error': 'Plan type is required'}), 400

        # Plan Configuration with base prices
        PLANS = {
            'basic': {
                'name': 'Basic Plan',
                'description': 'Essential tools for beginners',
                'base_price': 9.99
            },
            'professional': {
                'name': 'Professional Plan',
                'description': 'Advanced features for professionals',
                'base_price': 19.99
            },
            'premium': {
                'name': 'Premium Plan',
                'description': 'Complete automation for businesses',
                'base_price': 39.99
            }
        }

        # Validate plan type
        if plan_type not in PLANS:
            return jsonify({'error': 'Invalid plan type'}), 400

        # Create or get Stripe customer
        try:
            customer = stripe.Customer.list(email=current_user.email).data
            if customer:
                customer_id = customer[0].id
                logger.info(f"Using existing Stripe customer: {customer_id}")
            else:
                customer = stripe.Customer.create(
                    email=current_user.email,
                    metadata={'user_id': current_user.id})
                customer_id = customer.id
                logger.info(f"Created new Stripe customer: {customer_id}")
        except Exception as customer_error:
            logger.error(f"Error creating/retrieving customer: {customer_error}")
            # Continue without customer ID if there's an error
            customer_id = None

        # Define supported currencies
        supported_stripe_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']

        # Create Checkout Session with dynamic pricing
        currency_code = display_currency.lower() if display_currency.upper() in supported_stripe_currencies else 'usd'
        line_items = [{
            'price_data': {
                'currency': currency_code,
                'product_data': {
                    'name': PLANS[plan_type]['name'],
                    'description': PLANS[plan_type]['description'],
                },
                'unit_amount': int(PLANS[plan_type]['base_price'] * 100),
                'recurring': {
                    'interval': 'month'
                }
            },
            'quantity': 1,
        }]
        logger.info(f"Using dynamic price data: {PLANS[plan_type]['base_price']} {currency_code}")

        # Set up session parameters
        session_params = {
            'payment_method_types': ['card'],
            'line_items': line_items,
            'mode': 'subscription',
            'success_url': url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': url_for('payment_cancel', _external=True),
            'metadata': {
                'plan_type': plan_type,
                'user_id': str(current_user.id),
                'base_price': str(PLANS[plan_type]['base_price']),
                'display_currency': display_currency
            },
            'allow_promotion_codes': True,
            'billing_address_collection': 'required',
        }

        # Add customer ID if available
        if customer_id:
            session_params['customer'] = customer_id
            session_params['customer_update'] = {
                'address': 'auto',
                'name': 'auto'
            }

        # Set currency
        if display_currency.upper() in supported_stripe_currencies:
            session_params['currency'] = currency_code
        else:
            session_params['currency'] = 'usd'  # Default to USD if currency not supported

        logger.info(f"Creating Stripe checkout session with params: {json.dumps(session_params, default=str)}")
        session = stripe.checkout.Session.create(**session_params)
        logger.info(f"Checkout session created successfully: {session.id}, URL: {session.url}")

        return jsonify({'url': session.url})

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({'error': str(e.user_message) if hasattr(e, 'user_message') else str(e)}), 400
    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Server error processing payment: ' + str(e)}), 500


@app.route("/publish_content", methods=['POST'])
@login_required
def publish_content():
    """Publish generated content to WordPress site with plan limits"""
    try:
        # Get user's active subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id,
            status='active').order_by(SubscriptionPlan.id.desc()).first()

        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 403

        # Check post generation limits based on plan
        post_limits = {'free': 1, 'basic': 2, 'professional': 5, 'premium': 15}

        # Get current month's post count
        current_month_start = datetime.utcnow().replace(day=1,
                                                        hour=0,
                                                        minute=0,
                                                        second=0,
                                                        microsecond=0)

        # Get the latest WordPress installation
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id).order_by(
                WordPressInstallation.id.desc()).first()

        if not wp_install:
            return jsonify({'error': 'No WordPress installation found'}), 404

        # Initialize WordPress API client
        wp_api = WordPressRestAPI(base_url=f"https://{wp_install.site_url}",
                                  username=wp_install.admin_username,
                                  password=wp_install.admin_password)

        # Get post count from WordPress
        post_count = wp_api.get_post_count(current_month_start)
        post_limit = post_limits.get(subscription.plan_type, 1)

        if post_count >= post_limit:
            return jsonify({
                'success':
                False,
                'error':
                f'Monthly post limit ({post_limit}) reached for {subscription.plan_type} plan'
            }), 403

        # Get generated content from session
        title = session.get('generated_title', 'Generated Post')
        content = session.get('generated_content', '')

        # Create post as draft
        result = wp_api.create_post(title, content)

        if result:
            return jsonify({
                'success': True,
                'message':
                f'Content published successfully ({post_count + 1}/{post_limit} posts this month)',
                'post_id': result.get('id')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to publish content'
            }), 500

    except Exception as e:
        logger.error(f"Error publishing content: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/small_business")
def small_business():
    return render_template('solutions_small_business.html')


@app.route("/freelancers")
def freelancers():
    return render_template('solutions_freelancers.html')


@app.route("/agencies")
def agencies():
    return render_template('solutions_agencies.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            # Collect form data
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            attachments = request.files.getlist('attachments')

            # Validate inputs
            if not all([name, email, subject, message]):
                flash('Please fill out all fields', 'error')
                return render_template('contact.html')

            # Validate file uploads
            if len(attachments) > 5:
                flash('Maximum 5 files allowed', 'error')
                return render_template('contact.html')

            # Process file uploads
            uploaded_files = []
            for file in attachments:
                if file.filename:
                    try:
                        file_id = upload_file_to_storage(file)
                        file_url = url_for_uploaded_file(file_id)
                        uploaded_files.append(file_url)
                    except Exception as e:
                        logger.error(
                            f"Error uploading file {file.filename}: {e}")

            # Use LLM to help categorize and potentially draft a response
            categorization_schema = {
                'type': 'object',
                'properties': {
                    'category': {
                        'type':
                        'string',
                        'enum': [
                            'Technical Support', 'Sales Inquiry', 'Feedback',
                            'Partnership', 'Other'
                        ]
                    },
                    'priority': {
                        'type': 'string',
                        'enum': ['Low', 'Medium', 'High']
                    }
                },
                'required': ['category', 'priority']
            }

            categorization_result = llm(
                prompt=f"""Categorize this contact form submission:
                Name: {name}
                Email: {email}
                Subject: {subject}
                Message: {message}
                Attachments: {len(uploaded_files)} files
                """,
                response_schema=categorization_schema,
                model='gpt-4o-mini',
                temperature=0.5,
                image_url=None)

            # Log the contact form submission
            logger.info(
                f"Contact form submission from {email}: {subject}, Attachments: {len(uploaded_files)}"
            )

            flash('Thank you for your message! We will get back to you soon.',
                  'success')
            return redirect(url_for('contact'))

        return render_template('contact.html')

    except Exception as e:
        logger.error(f"Contact form error: {e}")
        flash('An error occurred. Please try again later.', 'error')
        return render_template('contact.html')


@app.route('/wordpress_automation_demo')
def wordpress_automation_demo():
    """Render the WordPress automation demo page"""
    try:
        return render_template('wordpress_automation_demo.html')
    except Exception as e:
        logger.error(f"Error rendering WordPress automation demo: {e}")
        flash('Error loading demo page')
        return redirect(url_for('home'))


@app.route('/glossary')
def glossary():
    """Render the technical glossary page"""
    try:
        return render_template('glossary.html')
    except Exception as e:
        logger.error(f"Error rendering glossary page: {e}")
        flash('Error loading glossary page')
        return redirect(url_for('home'))


@app.route("/blog")
def blog():
    """Render the blog page"""
    try:
        return render_template('blog.html')
    except Exception as e:
        logger.error(f"Error rendering blog page: {e}")
        flash('Error loading blog page')
        return redirect(url_for('home'))


@app.route("/tutorials")
def tutorials():
    """Render the tutorials page"""
    try:
        return render_template('tutorials.html')
    except Exception as e:
        logger.error(f"Error rendering tutorials page: {e}")
        flash('Error loading tutorials page')
        return redirect(url_for('home'))


@app.route("/case_studies")
def case_studies():
    """Render the case studies page"""
    try:
        return render_template('case_studies.html')
    except Exception as e:
        logger.error(f"Error rendering case studies page: {e}")
        flash('Error loading case studies page')
        return redirect(url_for('home'))


@app.route("/api/convert-currency", methods=["GET"])
def convert_currency():
    from flask import request, jsonify
    try:
        amount = request.args.get("amount", type=float)
        from_curr = request.args.get("from", default="USD")
        to_curr = request.args.get("to", default="USD")
        if amount is None:
            return jsonify({"error": "Amount is required"}), 400
        # Updated exchange rates as of 2024
        rates = {
            "USD": 1.0,  # 1 USD = base rate
            "EUR": 0.8688,  # 1 USD = 0.8688 EUR
            "GBP": 0.7438,  # 1 USD = 0.7438 GBP
            "INR": 84.5484,  # 1 USD = 84.5484 INR
            "JPY": 144.23,  # 1 USD = 144.23 JPY
            "AUD": 1.554,  # 1 USD = 1.554 AUD
            "CAD": 1.4266,  # 1 USD = 1.4266 CAD
            "CHF": 0.8276,  # 1 USD = 0.8276 CHF
            "CNY": 7.262,  # 1 USD = 7.262 CNY
            "HKD": 7.7637,  # 1 USD = 7.7637 HKD
            "NZD": 1.685,  # 1 USD = 1.685 NZD
            "SEK": 10.447,  # 1 USD = 10.447 SEK
            "KRW": 1424,  # 1 USD = 1424 KRW
            "SGD": 1.3429,  # 1 USD = 1.3429 SGD
            "NOK": 10.943,  # 1 USD = 10.943 NOK
            "MXN": 19.63,  # 1 USD = 19.63 MXN
            "LKR": 312.50,  # 1 USD = 312.50 LKR
            "BRL": 4.97,  # 1 USD = 4.97 BRL
            "ZAR": 18.89  # 1 USD = 18.89 ZAR
        }
        if from_curr not in rates:
            from_curr = "USD"
        if to_curr not in rates:
            to_curr = "USD"
        # Convert amount to target currency using exchange rates
        converted = amount * (rates[to_curr] / rates[from_curr])
        # Round to 2 decimal places
        return jsonify({"convertedAmount": round(converted, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from googletrans import Translator
import re

# Initialize translator
translator = Translator()


@app.route('/translate', methods=['POST'])
@limiter.limit("100 per minute")  # Higher limit for translations
def translate():
    data = request.get_json()
    text = data.get('text')
    target_lang = data.get('target', 'en')

    try:
        # Translate text
        translated = translator.translate(text, dest=target_lang)
        return jsonify({'translatedText': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/translate_website', methods=['POST'])
def translate_website():
    """Translate entire website content"""
    data = request.get_json()
    target_lang = data.get('target', 'en')

    try:
        # Collect all translatable elements from templates
        translatable_elements = []
        for template in os.listdir('templates'):
            with open(os.path.join('templates', template), 'r') as f:
                content = f.read()
                # Extract text elements that need translation
                translatable_elements.extend(
                    re.findall(r'data-translatable>([^<]+)', content))

        # Translate each element
        translated_website = {}
        for element in translatable_elements:
            # Use googletrans instead of argostranslate
            translator = Translator()
            translated_element = translator.translate(element,
                                                      dest=target_lang).text
            translated_website[element] = translated_element

        return jsonify(translated_website)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/generate_content', methods=['POST'])
@login_required
def generate_content_api():
    try:
        data = request.get_json()
        plan = data.get('plan')

        if not plan:
            return jsonify({'error': 'Plan is required'}), 400

        # Get category and menu items
        wp_install = WordPressInstallation.query.filter_by(
            server_id=current_user.server_connections[-1].id
        ).order_by(WordPressInstallation.id.desc()).first()

        if not wp_install or not wp_install.category_id:
            return jsonify({'error': 'Website category not found'}), 400

        category = WebsiteCategory.query.get(wp_install.category_id)
        menu_items = session.get('generated_menu_items', [])

        # Initialize Gemini Content Trainer
        trainer = GeminiContentTrainer()

        # Generate content based on plan
        generated_content = {}
        if plan == 'basic':
            generated_content = {
                'blog_post': generate_blog_post(trainer, category.name),
                'about_page': generate_about_page(trainer, category.name),
                'contact_page': generate_contact_page(trainer, category.name)
            }
        elif plan in ['professional', 'premium', 'enterprise']:
            generated_content = {
                'blog_posts': [generate_blog_post(trainer, category.name) for _ in range(5)],
                'all_pages': generate_all_pages(trainer, category.name, menu_items),
                'seo_content': generate_seo_content(trainer, category.name),
                'social_media': generate_social_media(trainer, category.name)
            }

        # Store generated content in session
        session['generated_content'] = generated_content

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500
@app.route('/api/check_gemini_api')
@login_required
def check_gemini_api():
    """Check if Gemini API key is configured"""
    try:
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({'configured': False})

        # Quick validation of API key format (not a full verification)
        if len(gemini_api_key) < 10 or not gemini_api_key.startswith('AI'):
            return jsonify({'configured': False, 'message': 'API key format appears invalid'})

        return jsonify({'configured': True})
    except Exception as e:
        logger.error(f"Error checking Gemini API: {e}")
        return jsonify({'configured': False, 'error': str(e)})